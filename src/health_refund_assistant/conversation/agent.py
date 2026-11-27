"""Objetivo: controlar o estado conversacional de tarefas de reembolso.

Entradas: texto do usuário, documento, exportação, estado anterior e evidências.
Processamento: identifica intenção, solicita entradas faltantes e executa ferramentas.
Saídas: resposta, estado da tarefa e evidências atualizadas.
"""

import re
from pathlib import Path
from typing import Any, Sequence

from ..plan.plan_exports import load_selected_exports
from .assistant import AssistantRequest, handle_request, atualizar_estimativa
from .resposta_assistente import create_assistant_answer
from .structured_ai import request_structured_json
from ..core.prompt_library import carregar_prompt, carregar_respostas_agente
from .task_registry import get_task_definition


TASK_STATES = {
    "aguardando_documento",
    "aguardando_exportacao",
    "aguardando_confirmacao",
    "analisando",
    "aguardando_revisao",
    "concluido",
}

TASK_DEFINITIONS = {
    "analisar_documento": {
        "entrada": ("documento", "exportacao_do_plano"),
        "resultado": "evidencias_documento_status_prazo",
    },
    "consultar_status": {
        "entrada": ("documento", "exportacao_do_plano"),
        "resultado": "status_pedido",
    },
    "confirmar_pagamento": {
        "entrada": ("numero_nota", "exportacao_do_plano"),
        "resultado": "confirmacao_pagamento",
    },
    "verificar_prazo": {
        "entrada": ("documento", "data_referencia"),
        "resultado": "prazo_simulado",
    },
    "revisar_completude": {
        "entrada": ("documento",),
        "resultado": "campos_faltantes",
    },
}


def mensagem_agente(chave: str, **valores: Any) -> str:
    """Resolve uma resposta de chat pelo prompt versionado do agente."""
    respostas = carregar_respostas_agente("v1.1")
    modelo = respostas.get(chave)
    if not isinstance(modelo, str) or not modelo.strip():
        raise ValueError(f"Resposta não definida no prompt do agente: {chave}")
    try:
        return modelo.format(**valores)
    except (KeyError, ValueError) as error:
        raise ValueError("Resposta do agente usa variável não fornecida.") from error


def executar_ferramenta(nome: str, **kwargs: Any) -> Any:
    """Registra ferramentas simples usadas pelo agente."""
    if nome == "extrair_e_conciliar":
        return handle_request(kwargs["request"])
    if nome == "consultar_exportacao":
        return buscar_nota_em_exportacoes(
            kwargs["referencia"],
            kwargs["export_paths"],
        )
    if nome == "responder_sobre_evidencias":
        return create_assistant_answer(
            kwargs["message"],
            kwargs["evidence"],
            "v1.2",
            kwargs.get("history", []),
        )
    raise ValueError(f"Ferramenta não registrada: {nome}")


def identificar_tarefa(texto: str) -> str:
    texto = texto.lower()
    if re.search(r"\b(ignore|reveal|revele|prompt|outro usuário|outros usuários|guardrails|sistema)\b", texto):
        return "categoria_nao_mapeada"
    if re.search(r"\b(prazo|dentro do prazo|vencido|venceu|atrasado|corte|quanto tempo)\b", texto):
        return "verificar_prazo"
    if re.search(r"\b(recebi|já recebi|foi pago|já foi pago|pagamento|pagaram|valor recebido)\b", texto):
        return "confirmar_pagamento"
    if re.search(r"\bstatus\b|\bpedido\b|\bandamento\b|solicit", texto):
        return "consultar_status"
    if re.search(r"\b(faltando|faltam|completo|completa|incomplet|campos|registro|crm)\b|não foi identificado", texto):
        return "revisar_completude"
    if re.search(r"\b(analis|nota|recibo|documento|pdf|imagem)\b", texto):
        return "analisar_documento"
    if not texto.strip():
        return "categoria_nao_mapeada"
    return "categoria_nao_mapeada"


def extrair_referencia_nota(texto: str) -> str | None:
    padroes = (
        r"\bnota\s*(?:n[ºo°]?\.?\s*)?#?\s*([a-z0-9][a-z0-9.-]{2,})",
        r"\bn[ºo°]\s*#?\s*([a-z0-9][a-z0-9.-]{2,})",
    )
    for padrao in padroes:
        match = re.search(padrao, texto.lower())
        if match:
            return match.group(1)
    return None


def _strings_planas(valor: Any) -> list[str]:
    if isinstance(valor, dict):
        return [item for chave in valor for item in _strings_planas(valor[chave])]
    if isinstance(valor, list):
        return [item for entry in valor for item in _strings_planas(entry)]
    return [str(valor)] if valor is not None else []


def buscar_nota_em_exportacoes(
    referencia: str,
    export_paths: Sequence[Path],
) -> dict[str, Any] | None:
    try:
        exports = load_selected_exports(list(export_paths))
    except (OSError, ValueError):
        return None
    referencia_normalizada = referencia.lower()
    for exportacao in exports:
        for reembolso in exportacao.get("reembolsos", []):
            if not isinstance(reembolso, dict):
                continue
            texto = " ".join(_strings_planas(reembolso)).lower()
            if referencia_normalizada not in texto:
                continue
            status = next(
                (
                    valor
                    for chave, valor in reembolso.items()
                    if isinstance(valor, (str, int, float))
                    and "status" in chave.lower()
                ),
                None,
            )
            pago = next(
                (
                    valor
                    for chave, valor in reembolso.items()
                    if isinstance(valor, (str, int, float))
                    and any(nome in chave.lower() for nome in ("paid", "pago", "reembols"))
                ),
                None,
            )
            return {
                "referencia": referencia,
                "status": status,
                "valor_pago": pago,
                "registro": reembolso,
            }
    return None


def novo_estado(texto: str = "") -> dict[str, Any]:
    return {
        "task": identificar_tarefa(texto),
        "status": "aguardando_documento" if texto else "aguardando_documento",
        "missing": ["documento"],
        "note_reference": extrair_referencia_nota(texto),
        "pending_question": None,
    }


def interpretar_pedido(
    texto: str,
    estado: dict[str, Any] | None,
    tem_documento: bool,
    tem_exportacao: bool,
) -> dict[str, Any]:
    """Usa GPT-6 Luna para interpretar intenção e entradas faltantes."""
    try:
        prompt, _ = carregar_prompt("agente_conversacional", "v1.1")
        interpretacao = request_structured_json(
            prompt,
            {
                "pedido_usuario": texto,
                "estado": estado or novo_estado(texto),
                "tem_documento": tem_documento,
                "tem_exportacao": tem_exportacao,
            },
            "agent_turn.schema.json",
        )
        if interpretacao.get("task") in {
            "analisar_documento",
            "consultar_status",
            "confirmar_pagamento",
            "verificar_prazo",
            "revisar_completude",
            "categoria_nao_mapeada",
        }:
            return interpretacao
    except (OSError, ValueError, RuntimeError):
        pass
    return {
        "task": identificar_tarefa(texto),
        "note_reference": extrair_referencia_nota(texto),
        "missing": [],
        "mensagem": None,
    }


def handle_agent_turn(
    message: str,
    agent_state: dict[str, Any] | None,
    evidence: dict[str, Any] | None,
    pdf_bytes: bytes | None = None,
    image_bytes: bytes | None = None,
    export_paths: Sequence[Path] = (),
    reference_date=None,
    deadline_days: int = 30,
) -> dict[str, Any]:
    """Processa uma rodada e devolve resposta, estado e evidências."""
    state = dict(agent_state or novo_estado(message))
    interpretacao = interpretar_pedido(
        message,
        state,
        bool(pdf_bytes or image_bytes),
        bool(export_paths),
    )
    task = interpretacao.get("task") or state.get("task", "analisar_documento")
    state["task"] = task
    note_reference = (
        interpretacao.get("note_reference")
        or extrair_referencia_nota(message)
        or state.get("note_reference")
    )
    state["note_reference"] = note_reference

    if (
        not pdf_bytes
        and not image_bytes
        and not export_paths
        and not evidence
        and task in {
            "analisar_documento",
            "consultar_status",
            "confirmar_pagamento",
        }
    ):
        state["status"] = "aguardando_exportacao"
        state["missing"] = ["exportacao_do_plano"]
        state["pending_question"] = "Envie ou importe a exportação atual do plano em JSON."
        return {
            "answer": mensagem_agente(
                "aguardando_exportacao_pagamento"
                if task == "confirmar_pagamento"
                else "aguardando_exportacao_geral"
            ),
            "evidence": evidence,
            "state": state,
        }

    if pdf_bytes or image_bytes:
        if not export_paths:
            state["status"] = "aguardando_exportacao"
            state["missing"] = ["exportacao_do_plano"]
            state["pending_question"] = "Envie a exportação atual do plano em JSON."
            return {
                "answer": mensagem_agente("documento_aguardando_exportacao"),
                "evidence": evidence,
                "state": state,
            }

        state["status"] = "analisando"
        state["pending_question"] = None
        request = AssistantRequest(
            pdf_bytes=pdf_bytes or b"",
            image_bytes=image_bytes or b"",
            question=message or "Analise este documento.",
            export_paths=export_paths,
            extraction_prompt_version="v4.2",
            response_prompt_version="v1.2",
            reference_date=reference_date,
            deadline_days=deadline_days,
        )
        result = executar_ferramenta("extrair_e_conciliar", request=request)
        evidence = {
            "documento": result.document_fields,
            "conciliacao": result.assessment,
            "revisao_ia": result.review,
        }
        state["status"] = "concluido"
        state["missing"] = []
        state["pending_question"] = None
        return {"answer": result.answer, "evidence": evidence, "state": state}

    if export_paths and not (pdf_bytes or image_bytes):
        if task == "confirmar_pagamento" or note_reference:
            resultado = executar_ferramenta(
                "consultar_exportacao",
                referencia=note_reference or "nota",
                export_paths=export_paths,
            )
            if resultado and note_reference:
                status = resultado.get("status") or "não informado"
                pago = resultado.get("valor_pago")
                valor = f" Valor registrado: {pago}." if pago is not None else ""
                state["status"] = "concluido"
                state["missing"] = []
                return {
                    "answer": mensagem_agente(
                        "pagamento_localizado",
                        note_reference=note_reference,
                        status=status,
                        valor=valor,
                    ),
                    "evidence": evidence,
                    "state": state,
                }
        state["status"] = "aguardando_documento"
        state["missing"] = ["documento"]
        return {
            "answer": mensagem_agente("exportacao_aguardando_documento"),
            "evidence": evidence,
            "state": state,
        }

    if evidence:
        if "revisao_ia" not in evidence:
            state["status"] = "aguardando_revisao"
            return {
                "answer": mensagem_agente("revisao_antiga"),
                "evidence": evidence,
                "state": state,
            }
        evidence = dict(evidence)
        assessment = dict(evidence["conciliacao"])
        if reference_date is not None:
            assessment = atualizar_estimativa(
                assessment,
                reference_date,
                "v1.0",
            )
        evidence["conciliacao"] = assessment
        answer = executar_ferramenta(
            "responder_sobre_evidencias",
            message=message,
            evidence=evidence,
            history=[],
        )
        state["status"] = "concluido"
        state["missing"] = []
        return {"answer": answer, "evidence": evidence, "state": state}

    if task == "categoria_nao_mapeada":
        state["status"] = "aguardando_confirmacao"
        state["missing"] = ["confirmacao_usuario"]
        state["pending_question"] = mensagem_agente("categoria_nao_mapeada")
        return {
            "answer": mensagem_agente("categoria_nao_mapeada"),
            "evidence": None,
            "state": state,
        }

    if task == "confirmar_pagamento":
        state["status"] = "aguardando_documento"
        state["missing"] = ["documento", "exportacao_do_plano"]
        return {
            "answer": mensagem_agente("confirmar_pagamento_sem_dados"),
            "evidence": None,
            "state": state,
        }
    if task == "consultar_status":
        state["status"] = "aguardando_documento"
        state["missing"] = ["documento", "exportacao_do_plano"]
        return {
            "answer": mensagem_agente("consultar_status_sem_dados"),
            "evidence": None,
            "state": state,
        }
    if task == "verificar_prazo":
        state["status"] = "aguardando_documento"
        state["missing"] = ["documento"]
        return {
            "answer": mensagem_agente("verificar_prazo_sem_dados"),
            "evidence": None,
            "state": state,
        }
    if task == "revisar_completude":
        state["status"] = "aguardando_documento"
        state["missing"] = ["documento"]
        return {
            "answer": mensagem_agente("revisar_completude_sem_dados"),
            "evidence": None,
            "state": state,
        }

    state["status"] = "aguardando_documento"
    state["missing"] = ["documento"]
    return {
        "answer": mensagem_agente("fallback_analise"),
        "evidence": None,
        "state": state,
    }
