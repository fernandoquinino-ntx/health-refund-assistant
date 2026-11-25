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

from .assistant import AssistantRequest, ExtractionError, handle_request
from .assessment import DEADLINE_DAYS, ExportPeriodError
from .paths import INCOMING_DIR, PROMPTS_DIR
from .plan_exports import available_plan_exports, import_plan_export


ASSISTANT_PROMPTS_DIR = PROMPTS_DIR / "reembolso_assistente"


def prompt_versions(directory: Path) -> List[str]:
    return sorted(
        (path.stem for path in directory.glob("v*.txt")),
        key=lambda version: tuple(
            int(part) for part in version.removeprefix("v").split(".")
        ),
    )


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
    first, second = st.columns(2)
    first.metric("Situação do pedido", assessment["situacao_pedido"])
    second.metric("Prazo simulado", assessment["situacao_prazo"])
    st.caption(
        f"Data de referência: {assessment['data_referencia']} · "
        f"Base do prazo: {assessment['data_base_prazo'] or 'indeterminada'} "
        f"({assessment['origem_data_base_prazo'] or 'sem data'}) · "
        f"{assessment['dias_desde_atendimento_ou_emissao']} dia(s)"
    )
    st.info(assessment["aviso_prazo"])

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
        "Envie uma nota, selecione os datasets exportados do plano e pergunte "
        "sobre o status. A análise de prazo de 30 dias é somente uma simulação."
    )

    extraction_versions = prompt_versions(PROMPTS_DIR / "vlm_extractor")
    assistant_versions = prompt_versions(ASSISTANT_PROMPTS_DIR)
    if not extraction_versions or not assistant_versions:
        st.error("Não encontrei as versões necessárias da biblioteca de prompts.")
        return

    with st.sidebar:
        st.header("Prompts e avaliação")
        extraction_version = st.selectbox(
            "Prompt de extração",
            extraction_versions,
            index=extraction_versions.index("v4.0")
            if "v4.0" in extraction_versions
            else len(extraction_versions) - 1,
        )
        assistant_version = st.selectbox(
            "Prompt do assistente",
            assistant_versions,
            index=len(assistant_versions) - 1,
        )
        prompt_path = PROMPTS_DIR / "vlm_extractor" / f"{extraction_version}.txt"
        with st.expander("Ver prompt de extração"):
            st.code(prompt_path.read_text(encoding="utf-8"), language="text")
        assistant_prompt_path = ASSISTANT_PROMPTS_DIR / f"{assistant_version}.txt"
        with st.expander("Ver prompt do assistente"):
            st.code(assistant_prompt_path.read_text(encoding="utf-8"), language="text")
        reference_date = st.date_input(
            "Data de referência",
            value=datetime.now(ZoneInfo("America/Sao_Paulo")).date(),
            help="A data permite repetir cenários de teste; no uso normal, mantenha hoje.",
        )
        deadline_days = st.number_input(
            "Prazo simulado (dias)",
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

    st.subheader("2. Selecionar nota e fazer uma pergunta")
    source = st.radio(
        "Onde está o PDF?",
        ("Enviar pelo navegador", "Escolher em data/incoming/"),
        horizontal=True,
    )
    pdf_upload = None
    pdf_path = None
    if source == "Enviar pelo navegador":
        pdf_upload = st.file_uploader("Nota fiscal ou recibo (PDF)", type=["pdf"])
    else:
        local_pdfs = get_local_pdfs()
        if local_pdfs:
            pdf_path = st.selectbox(
                "PDFs em data/incoming/",
                options=local_pdfs,
                format_func=lambda value: value.name,
            )
        else:
            st.info("Coloque um PDF em data/incoming/ ou escolha upload pelo navegador.")
    question = st.text_area(
        "Sua pergunta",
        value="Este reembolso já foi solicitado ou pago? Há alguma informação faltando?",
        height=90,
    )

    if st.button("Analisar documento", type="primary"):
        if not pdf_upload and not pdf_path:
            st.error("Selecione um PDF para analisar.")
        elif not question.strip():
            st.error("Escreva uma pergunta para o assistente.")
        elif not selected_paths:
            st.error(
                "Selecione ao menos uma exportação do plano; a análise não foi executada."
            )
        else:
            try:
                pdf_bytes = (
                    pdf_upload.getvalue()
                    if pdf_upload is not None
                    else pdf_path.read_bytes()
                )
                request = AssistantRequest(
                    pdf_bytes=pdf_bytes,
                    question=question,
                    export_paths=[Path(path) for path in selected_paths],
                    extraction_prompt_version=extraction_version,
                    response_prompt_version=assistant_version,
                    reference_date=reference_date,
                    deadline_days=int(deadline_days),
                )
                with st.spinner("Extraindo e avaliando o documento…"):
                    response = handle_request(request)
                st.subheader("Extração")
                st.json(response.document_fields)
                _show_assessment(response.assessment)
                st.subheader("Resposta")
                st.write(response.answer)
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
