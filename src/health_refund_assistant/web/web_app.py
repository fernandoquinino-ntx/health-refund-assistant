"""Objetivo: apresentar a interface Streamlit do assistente.

Entradas: PDFs, exportações, perguntas e opções fornecidas pelo usuário.
Processamento: coordena a conversa e chama os fluxos de análise.
Saídas: respostas e evidências na interface e estado de conversa local.
"""

import hashlib
import json
import time
from datetime import datetime
from pathlib import Path
from typing import List
from zoneinfo import ZoneInfo

import streamlit as st
from openai import APIError

from ..conversation.assistant import (
    AssistantRequest,
    ExtractionError,
    create_assistant_answer,
    handle_request,
    atualizar_estimativa,
)
from ..plan.assessment import DEADLINE_DAYS, ExportPeriodError
from ..conversation.conversation_memory import clear_conversation, load_conversation, save_conversation
from ..conversation.conversation_memory import conversation_path_for_user
from ..auth.local_auth import (
    DEFAULT_TEST_PIN,
    DEFAULT_TEST_USER,
    add_local_user,
    ensure_default_test_user,
    validate_local_user,
)
from ..core.trace import append_trace_event, load_trace_events, text_hash
from ..conversation.agent import handle_agent_turn
from ..core.paths import INCOMING_DIR, PROMPTS_DIR
from ..core.prompt_library import prompt_versions
from ..plan.plan_exports import (
    available_plan_exports,
    export_assessment_json,
    import_assessment_json,
    import_plan_export,
    latest_export_status,
)


ASSISTANT_PROMPTS_DIR = PROMPTS_DIR / "reembolso_assistente"


def get_local_pdfs() -> List[Path]:
    INCOMING_DIR.mkdir(parents=True, exist_ok=True)
    return sorted(
        (
            path
            for path in INCOMING_DIR.iterdir()
            if path.is_file() and path.suffix.lower() == ".pdf"
        ),
        reverse=True,
    )


def _show_assessment(assessment: dict) -> None:
    if assessment.get("regras_prazo_confirmadas") is True:
        corte_d2 = assessment.get("corte_d2", {})
        prazo_365 = assessment.get("prazo_365", {})
        if corte_d2.get("ativo"):
            st.caption(
                f"D-2 confirmado: corte {corte_d2['corte_exportacao']} "
                f"({corte_d2['situacao']})."
            )
        if prazo_365.get("ativo"):
            st.caption(
                f"365 dias confirmado: prazo final {prazo_365['prazo_final']} "
                f"({prazo_365['dias_restantes']} dia(s) restantes)."
            )
    if assessment.get("candidatos"):
        assessment = {
            **assessment,
            "situacao_prazo": "nao_aplicavel_pedido_localizado",
            "aviso_prazo": "Prazo de envio não analisado para pedido localizado.",
        }
    first, second = st.columns(2)
    first.metric("Situação do pedido", assessment["situacao_pedido"])
    second.metric("Prazo de envio (simulação)", assessment["situacao_prazo"])
    if assessment["situacao_prazo"] != "nao_aplicavel_pedido_localizado":
        st.caption(
            f"Data de referência: {assessment['data_referencia']} · "
            f"Base do prazo: {assessment['data_base_prazo'] or 'indeterminada'} "
            f"({assessment['origem_data_base_prazo'] or 'sem data'}) · "
            f"{assessment['dias_desde_atendimento_ou_emissao']} dia(s)"
        )
    st.info(assessment["aviso_prazo"])
    estimate = assessment.get("estimativa_pagamento")
    if estimate:
        st.subheader("Estimativa de processamento")
        if estimate["situacao"] == "nao_e_possivel_estimar":
            st.warning("Não é possível estimar: " + estimate["motivo"])
        else:
            st.write(
                f"Data estimada: {estimate['data_estimada']} · "
                f"Referência: {estimate['data_referencia']} · "
                f"Dias úteis restantes: {estimate['dias_uteis_restantes']} · "
                f"Dias úteis de atraso: {estimate['dias_uteis_atraso']} · "
                f"Situação: {estimate['situacao']}"
            )
        st.caption(estimate["aviso"])
    eligibility = assessment.get("elegibilidade")
    if eligibility:
        st.warning(
            "Elegibilidade: não é possível avaliar. " + eligibility["motivo"]
        )

    if assessment["campos_incompletos"]:
        st.warning(
            "Nota incompleta: "
            + ", ".join(assessment["campos_incompletos"])
            + ". A correspondência e a elegibilidade podem não ser conclusivas."
        )
    if assessment["periodo_dos_datasets_cobre_data_base"] is False:
        st.warning(
            "A data do documento não está coberta pelos períodos exportados. "
            "Não é possível concluir que o pedido não foi enviado; importe uma "
            "exportação que cubra essa data."
        )
    if assessment["erros_exportacao"]:
        st.warning(
            "A exportação contém erros de coleta; ausência de correspondência "
            "não é conclusiva."
        )

    if assessment["candidatos"]:
        st.subheader("Pedidos correspondentes para revisão")
        st.dataframe(
            [
                {
                    "Número do pedido": item["claim_number"],
                    "Beneficiário": item["beneficiary"],
                    "Prestador": item["provider"],
                    "Status no plano": item["portal_status"],
                    "Situação financeira": item["financial_status"],
                    "Solicitado": item["requested_amount"],
                    "Reembolsado": item["paid_amount"],
                    "Data do pagamento": item["payment_date"],
                    "Confiança": item["match_confidence"],
                }
                for item in assessment["candidatos"]
            ],
            use_container_width=True,
        )
    elif assessment["situacao_pedido"] == "nao_localizado_nas_exportacoes":
        st.info(
            "Nenhum pedido correspondente foi localizado nos arquivos e períodos "
            "selecionados. Isso não prova que o pedido nunca foi enviado."
        )


def reset_agent_session(session_state: dict) -> None:
    """Limpa conversa e anexos pendentes ao iniciar uma nova tarefa."""
    session_state["conversation"] = {
        "messages": [],
        "evidence": None,
        "agent": None,
    }
    session_state.pop("pending_pdf", None)
    session_state.pop("pending_image", None)
    session_state.pop("pending_export_paths", None)


def local_user_login() -> str | None:
    """Autentica ou cria um usuário local antes de carregar dados privados."""
    ensure_default_test_user()
    authenticated = st.session_state.get("authenticated_user")
    if isinstance(authenticated, str):
        return authenticated

    st.sidebar.subheader("Identidade local")
    st.sidebar.caption(
        f"Usuário padrão de teste: {DEFAULT_TEST_USER} / PIN {DEFAULT_TEST_PIN}"
    )
    create, login = st.sidebar.tabs(["Entrar", "Criar usuário"])
    with create:
        user_id = st.text_input("Usuário", key="create_local_user")
        pin = st.text_input("PIN", type="password", key="create_local_pin")
        if st.button("Criar usuário local"):
            try:
                normalized = add_local_user(user_id, pin)
            except ValueError as error:
                st.error(str(error))
            else:
                st.session_state["authenticated_user"] = normalized
                st.success("Usuário criado e autenticado.")
                st.rerun()
    with login:
        user_id = st.text_input("Usuário", key="login_local_user")
        pin = st.text_input("PIN", type="password", key="login_local_pin")
        if st.button("Entrar"):
            normalized = validate_local_user(user_id, pin)
            if normalized is None:
                st.error("Não foi possível validar o usuário.")
            else:
                st.session_state["authenticated_user"] = normalized
                st.success("Usuário autenticado.")
                st.rerun()
    st.info("A autenticação local é para isolamento de teste, não para produção.")
    st.stop()
    return None


def main() -> None:
    st.set_page_config(
        page_title="Assistente de reembolsos",
        page_icon="🩺",
        layout="centered",
    )
    authenticated_user = local_user_login()
    conversation_path = conversation_path_for_user(authenticated_user)
    if "conversation" not in st.session_state:
        try:
            st.session_state["conversation"] = load_conversation(conversation_path)
        except ValueError as error:
            st.error(str(error))
            st.stop()

    extraction_versions = prompt_versions(PROMPTS_DIR / "vlm_extractor")
    assistant_versions = prompt_versions(ASSISTANT_PROMPTS_DIR)
    review_versions = prompt_versions(PROMPTS_DIR / "revisao_documental")
    payment_versions = prompt_versions(PROMPTS_DIR / "estimativa_pagamento")
    if not all((extraction_versions, assistant_versions, review_versions, payment_versions)):
        st.error("Não encontrei as versões necessárias da biblioteca de prompts.")
        return

    extraction_version = extraction_versions[-1]
    assistant_version = assistant_versions[-1]
    review_version = review_versions[-1]
    payment_version = payment_versions[-1]
    reference_date = datetime.now(ZoneInfo("America/Sao_Paulo")).date()
    deadline_days = DEADLINE_DAYS

    with st.sidebar:
        if st.button("Nova conversa"):
            try:
                clear_conversation(conversation_path)
            except OSError as error:
                st.error(f"Não foi possível apagar a conversa: {error}")
            else:
                reset_agent_session(st.session_state)
                st.session_state.pop("pending_export_paths", None)
                st.rerun()
        if st.button("Sair"):
            st.session_state.pop("authenticated_user", None)
            st.session_state.pop("conversation", None)
            st.rerun()
        with st.expander("Auditoria local"):
            eventos = load_trace_events(authenticated_user)
            if eventos:
                st.dataframe(eventos[-20:], use_container_width=True)
            else:
                st.caption("Nenhuma interação registrada ainda.")

    conversation = st.session_state["conversation"]
    if not conversation["messages"]:
        with st.chat_message("assistant"):
            st.write(
                "Olá! Posso consultar status, pagamento, prazo ou verificar uma "
                "nota. Quando precisar de dados do plano ou de um documento, "
                "vou pedir apenas o arquivo necessário."
            )
    for message in conversation["messages"]:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    evidence = conversation["evidence"]
    if evidence:
        with st.expander("Ver detalhes da análise"):
            st.json(evidence)

    state = conversation.get("agent") or {}
    if state.get("status") == "aguardando_exportacao":
        export_upload = st.file_uploader(
            "Envie a exportação atual do plano em JSON",
            type=["json"],
            accept_multiple_files=False,
            key=f"export_upload_{st.session_state.get('upload_version', 0)}",
        )
        if export_upload is not None:
            try:
                path = import_plan_export(export_upload.name, export_upload.getvalue())
                st.session_state["pending_export_paths"] = [str(path)]
                st.success("Exportação importada. Continue no chat.")
                st.session_state["upload_version"] = (
                    st.session_state.get("upload_version", 0) + 1
                )
                st.rerun()
            except (ExportPeriodError, OSError, ValueError) as error:
                st.error(str(error))
    elif state.get("status") in {"aguardando_documento", "aguardando_revisao"}:
        document_upload = st.file_uploader(
            "Envie a nota fiscal ou o recibo",
            type=["pdf", "png", "jpg", "jpeg"],
            accept_multiple_files=False,
            key=f"document_upload_{st.session_state.get('upload_version', 0)}",
        )
        if document_upload is not None:
            suffix = Path(document_upload.name).suffix.lower()
            content = document_upload.getvalue()
            if suffix == ".pdf":
                st.session_state["pending_pdf"] = content
            else:
                st.session_state["pending_image"] = content
            st.success("Documento recebido. Continue no chat.")
            st.session_state["upload_version"] = (
                st.session_state.get("upload_version", 0) + 1
            )
            st.rerun()

    question = st.chat_input("Fale com o assistente sobre seu reembolso")
    if question is not None:
        if question.strip():
            try:
                history = conversation["messages"]
                pdf_bytes = st.session_state.pop("pending_pdf", None)
                image_bytes = st.session_state.pop("pending_image", None)
                pending_exports = st.session_state.pop("pending_export_paths", [])
                import_paths = [
                    Path(path) for path in pending_exports
                    if Path(path).is_file()
                ]
                if not import_paths:
                    export_status = latest_export_status(
                        datetime.now(ZoneInfo("America/Sao_Paulo"))
                    )
                    if export_status["atualizada"]:
                        import_paths = [Path(export_status["caminho"])]
                attachment_items = []
                evidence_for_turn = evidence

                with st.spinner("O agente está verificando a solicitação…"):
                    started_at = time.monotonic()
                    result = handle_agent_turn(
                        message=question,
                        agent_state=conversation.get("agent"),
                        evidence=evidence_for_turn,
                        pdf_bytes=pdf_bytes,
                        image_bytes=image_bytes,
                        export_paths=import_paths,
                        reference_date=reference_date,
                        deadline_days=int(deadline_days),
                    )
                    elapsed_ms = int((time.monotonic() - started_at) * 1000)

                if result["state"].get("status") == "aguardando_exportacao":
                    if pdf_bytes:
                        st.session_state["pending_pdf"] = pdf_bytes
                    if image_bytes:
                        st.session_state["pending_image"] = image_bytes
                elif result["state"].get("status") == "concluido":
                    st.session_state.pop("pending_pdf", None)
                    st.session_state.pop("pending_image", None)
                    st.session_state.pop("pending_export_paths", None)

                messages = history + [
                    {"role": "user", "content": question or "Documento anexado"},
                    {"role": "assistant", "content": result["answer"]},
                ]
                save_conversation(
                    messages,
                    result["evidence"],
                    path=conversation_path,
                    agent=result["state"],
                )
                append_trace_event(
                    authenticated_user,
                    {
                        "task": result["state"].get("task"),
                        "status": result["state"].get("status"),
                        "prompt_versions": {
                            "extraction": extraction_version,
                            "assistant": assistant_version,
                            "review": review_version,
                            "payment": payment_version,
                        },
                        "input_hash": text_hash(question),
                        "attachment_hashes": [
                            hashlib.sha256(attachment.getvalue()).hexdigest()
                            for attachment in attachment_items
                        ],
                        "output_hash": text_hash(result["answer"]),
                        "duration_ms": elapsed_ms,
                        "error": None,
                    },
                )
                st.session_state["conversation"] = load_conversation(conversation_path)
                st.session_state["upload_version"] = (
                    st.session_state.get("upload_version", 0) + 1
                )
                st.rerun()
            except ExtractionError as error:
                st.error(str(error))
            except (OSError, ValueError, ExportPeriodError) as error:
                st.error(str(error))
            except APIError as error:
                status_code = getattr(error, "status_code", None)
                st.error(
                    "A chamada à API OpenAI falhou"
                    + (f" (HTTP {status_code})." if status_code else ".")
                    + " Verifique OPENAPI_TOKEN, acesso ao modelo e conectividade."
                )
            except RuntimeError as error:
                st.error(str(error))


if __name__ == "__main__":
    main()
