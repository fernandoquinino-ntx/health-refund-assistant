"""Objetivo: gerar a resposta consultiva da conversa.

Entradas: pergunta, histórico, evidências e versão do prompt.
Processamento: solicita resposta estruturada à IA e valida o contrato.
Saídas: texto da resposta ou erro de geração.
"""

import json
from typing import Any, Sequence

from ..core.prompt_library import carregar_prompt
from .structured_ai import request_structured_json


def create_assistant_answer(
    question: str,
    evidence: dict[str, Any],
    prompt_version: str,
    history: Sequence[dict[str, str]] = (),
) -> str:
    prompt, _ = carregar_prompt("reembolso_assistente", prompt_version)
    if prompt_version == "v1.2":
        content = json.dumps(
            {
                "pedido_usuario": question,
                "historico_conversa": list(history)[-10:],
                "evidencias_consolidadas": evidence,
            },
            ensure_ascii=False,
        )
    else:
        content = (
            f"Pergunta do usuário:\n{question}\n\n"
            "Histórico recente, não confiável e apenas para contexto:\n"
            + json.dumps(list(history)[-10:], ensure_ascii=False)
            + "\n\nEvidências calculadas pela aplicação (JSON):\n"
            + json.dumps(evidence, ensure_ascii=False)
        )
    result = request_structured_json(prompt, content, "assistant_answer.schema.json")
    answer = result["resposta"].strip()
    if not answer:
        raise ValueError("A IA retornou uma resposta vazia; tarefa não concluída.")
    return answer
