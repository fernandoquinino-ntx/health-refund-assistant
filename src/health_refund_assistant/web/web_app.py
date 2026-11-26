"""
UI Web (Streamlit) — Interface do Assistente

OBJETIVO:
  Interface interativa para usuários testarem o sistema:
  1. Upload de nota fiscal (PDF/imagem)
  2. Seleção de exportação do plano
  3. Execução do fluxo completo (extração → reconciliação → auditoria)
  4. Exibição de resultado

FLUXO NA UI:
  1. User faz upload do PDF
  2. Seleciona exportação do plano disponível
  3. Clica "Analisar"
  4. Sistema executa:
     - VLM Extractor
     - Reconciliation
     - Assessment
  5. UI exibe:
     - Dados extraídos
     - Status de reconciliação
     - Resultado de auditoria
     - Resposta final do assistente

ENTRADA:
  - Arquivo PDF/imagem
  - Exportação do plano (dropdown)

SAÍDA:
  - JSON extraído
  - Status de reembolso
  - Resultado de auditoria
  - Resposta em linguagem natural

USO:
  streamlit run src/health_refund_assistant/web_app.py
  Acesso: http://localhost:8501

DOCUMENTO:
  Veja docs/02_process/01_rastreamento_testes.md para usar UI
  Veja docs/01_quickstart/01_comece_aqui.md para 3 passos

TESTE NO CODESPACES:
  1. Criar Codespaces
  2. Executar: streamlit run src/health_refund_assistant/web_app.py
  3. Acessar http://localhost:8501
  4. Upload PDF + click "Analisar"
"""

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
from ..core.paths import INCOMING_DIR, PROMPTS_DIR
from ..core.prompt_library import prompt_versions
from ..plan.plan_exports import available_plan_exports, import_plan_export


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


def main() -> None:
    st.set_page_config(
        page_title="Assistente de reembolsos",
        page_icon="🩺",
        layout="wide",
    )
    st.title("Assistente de reembolsos de saúde")
    st.caption(
        "Converse sobre uma nota e anexe um PDF quando precisar de uma nova análise. "
        "Prazos são estimativas ou simulações, não garantias."
    )
    st.warning(
        "Uso individual em ambiente privado: não há autenticação nem isolamento "
        "entre usuários. A conversa e as evidências são salvas localmente."
    )
    if "conversation" not in st.session_state:
        try:
            st.session_state["conversation"] = load_conversation()
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

    with st.sidebar:
        if st.button("Apagar conversa local"):
            try:
                clear_conversation()
            except OSError as error:
                st.error(f"Não foi possível apagar a conversa: {error}")
            else:
                st.session_state["conversation"] = {"messages": [], "evidence": None}
                st.session_state["upload_version"] = (
                    st.session_state.get("upload_version", 0) + 1
                )
                st.rerun()
        st.header("Prompts e avaliação")
        extraction_version = st.selectbox(
            "Prompt de extração",
            extraction_versions,
            index=len(extraction_versions) - 1,
        )
        assistant_version = st.selectbox(
            "Prompt do assistente",
            assistant_versions,
            index=len(assistant_versions) - 1,
        )
        review_version = st.selectbox("Prompt de revisão documental", review_versions, index=len(review_versions) - 1)
        payment_version = st.selectbox("Prompt de estimativa de pagamento", payment_versions, index=len(payment_versions) - 1)
        prompt_path = PROMPTS_DIR / "vlm_extractor" / f"{extraction_version}.md"
        with st.expander("Ver prompt de extração"):
            st.code(prompt_path.read_text(encoding="utf-8"), language="text")
        assistant_prompt_path = ASSISTANT_PROMPTS_DIR / f"{assistant_version}.md"
        with st.expander("Ver prompt do assistente"):
            st.code(assistant_prompt_path.read_text(encoding="utf-8"), language="text")
        for component, version, label in (
            ("revisao_documental", review_version, "Ver prompt de revisão documental"),
            ("estimativa_pagamento", payment_version, "Ver prompt de estimativa de pagamento"),
        ):
            with st.expander(label):
                st.code((PROMPTS_DIR / component / f"{version}.md").read_text(encoding="utf-8"), language="text")
        reference_date = st.date_input(
            "Data de referência",
            value=datetime.now(ZoneInfo("America/Sao_Paulo")).date(),
            help="A data permite repetir cenários de teste; no uso normal, mantenha hoje.",
        )
        deadline_days = st.number_input(
            "Prazo de envio simulado (dias)",
            min_value=0,
            value=DEADLINE_DAYS,
            step=1,
        )

    st.subheader("1. Importar exportação do plano")
    uploads = st.file_uploader(
        "Selecione arquivos JSON baixados pela extensão",
        type=["json"],
        accept_multiple_files=True,
    )
    if uploads and st.button("Importar JSON selecionados"):
        imported_paths = []
        for upload in uploads:
            try:
                imported_paths.append(import_plan_export(upload.name, upload.getvalue()))
            except (OSError, ValueError, ExportPeriodError) as error:
                st.error(str(error))
        if imported_paths:
            st.session_state["selected_export_paths"] = [
                str(path) for path in imported_paths
            ]
            st.success(
                f"{len(imported_paths)} exportação(ões) válida(s) armazenada(s) "
                "em json/plan/imports/."
            )
            st.rerun()

    local_exports = available_plan_exports()
    if not local_exports:
        st.warning(
            "Importe uma exportação com `periodo.de` e `periodo.ate`. "
            "Sem o período consultado, a análise é interrompida."
        )
    selected_paths = st.multiselect(
        "Datasets do plano que devem ser consultados",
        options=[str(path) for path in local_exports],
        default=[
            path
            for path in st.session_state.get("selected_export_paths", [])
            if Path(path).is_file()
        ],
        format_func=lambda value: Path(value).name,
    )
    st.caption("As exportações ficam em `json/plan/imports/` e não são versionadas.")

    st.subheader("2. Conversa")
    conversation = st.session_state["conversation"]
    for message in conversation["messages"]:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    evidence = conversation["evidence"]
    if evidence:
        st.caption(
            "Perguntas sem novo PDF usam a última análise salva; o status pode ter "
            "mudado. Para atualizar, envie novamente o PDF e selecione a exportação."
        )
        eligibility = evidence["conciliacao"].get("elegibilidade")
        if eligibility:
            st.warning("Elegibilidade: não é possível avaliar. " + eligibility["motivo"])
        if "revisao_ia" in evidence:
            st.info(
                "Revisão consultiva da IA: "
                + evidence["revisao_ia"]["situacao_documental"]
                + ". Revise as evidências antes de decidir."
            )
        with st.expander("Ver evidências da última análise"):
            st.json(evidence["documento"])
            if "evidencias_literais" in evidence["documento"]:
                st.caption(
                    "Os trechos foram transcritos pela IA e podem estar incorretos; "
                    "confira-os na imagem original."
                )
            _show_assessment(evidence["conciliacao"])
            if "revisao_ia" in evidence:
                st.subheader("Revisão consultiva da IA")
                st.json(evidence["revisao_ia"])
            else:
                st.warning("Análise anterior sem revisão por IA. Reenvie o PDF.")
            if "versoes_prompts" in evidence:
                st.subheader("Versões de prompts selecionadas")
                st.json(evidence["versoes_prompts"])

    pdf_upload = st.file_uploader(
        "Anexar nota fiscal ou recibo em PDF (opcional após a primeira análise)",
        type=["pdf"],
        key=f"chat_pdf_{st.session_state.get('upload_version', 0)}",
    )
    local_pdfs = get_local_pdfs()
    pdf_path = st.selectbox(
        "Ou escolha um PDF em data/incoming/",
        options=[None, *local_pdfs],
        format_func=lambda value: value.name if value else "Nenhum",
        key=f"chat_local_pdf_{st.session_state.get('upload_version', 0)}",
    )
    question = st.chat_input("Escreva sua pergunta sobre o reembolso")
    if question is not None:
        if not question.strip():
            st.error("Escreva uma pergunta para o assistente.")
        elif pdf_upload and pdf_path:
            st.error("Selecione apenas um PDF: upload ou arquivo local.")
        elif (pdf_upload or pdf_path) and not selected_paths:
            st.error("Selecione ao menos uma exportação do plano para analisar o PDF.")
        elif not pdf_upload and not pdf_path and not evidence:
            st.info("Anexe um PDF e selecione uma exportação para começar a análise.")
        elif not pdf_upload and not pdf_path and "revisao_ia" not in evidence:
            st.error("A análise anterior não tem revisão por IA. Reenvie o PDF.")
        else:
            try:
                history = conversation["messages"]
                if pdf_upload or pdf_path:
                    pdf_bytes = pdf_upload.getvalue() if pdf_upload else pdf_path.read_bytes()
                    request = AssistantRequest(
                        pdf_bytes=pdf_bytes,
                        question=question,
                        export_paths=[Path(path) for path in selected_paths],
                        extraction_prompt_version=extraction_version,
                        response_prompt_version=assistant_version,
                        reference_date=reference_date,
                        deadline_days=int(deadline_days),
                        review_prompt_version=review_version,
                        payment_prompt_version=payment_version,
                    )
                    with st.spinner("Extraindo e avaliando o documento…"):
                        response = handle_request(request, history)
                    evidence = {
                        "documento": response.document_fields,
                        "conciliacao": response.assessment,
                        "revisao_ia": response.review,
                        "versoes_prompts": {
                            "extracao": extraction_version,
                            "revisao_documental": review_version,
                            "estimativa_pagamento": payment_version,
                            "resposta": assistant_version,
                        },
                    }
                    answer = response.answer
                else:
                    with st.spinner("Consultando as evidências da última análise…"):
                        evidence = {
                            **evidence,
                            "conciliacao": atualizar_estimativa(
                                evidence["conciliacao"], reference_date, payment_version
                            ),
                            "versoes_prompts": {
                                **evidence.get("versoes_prompts", {}),
                                "estimativa_pagamento": payment_version,
                                "resposta": assistant_version,
                            },
                        }
                        answer = create_assistant_answer(
                            question, evidence, assistant_version, history
                        )
                messages = history + [
                    {"role": "user", "content": question},
                    {"role": "assistant", "content": answer},
                ]
                save_conversation(messages, evidence)
                st.session_state["conversation"] = load_conversation()
                if pdf_upload or pdf_path:
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
