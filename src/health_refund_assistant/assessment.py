"""
Auditor (Verificador de Completude e Prazos)

OBJETIVO:
  Auditoria pré-envio de notas NÃO encontradas na exportação.
  Valida campos obrigatórios e prazos de submissão (365 dias).

ENTRADA:
  - Dados extraídos (JSON)
  - Status de reconciliação ("não encontrado")

SAÍDA:
  - Resultado de auditoria:
    * COMPLETO: Todos campos obrigatórios presentes
    * INCOMPLETO: Faltam campos (nome, CRM/CRN, descrição, valor, data)
    * PRAZO_VENCIDO: Nota com >365 dias (inelegível para submissão)
    * ELEGIVEL: Pronto para submissão à concierge

PROCESSO (ETAPA 3 DO FLUXO):
  JSON extraído → Assessment → Auditoria pré-envio

CAMPOS OBRIGATÓRIOS (Auditoria):
  1. nome_profissional ou crm/crn
  2. descricao_servico
  3. cnpj_cpf_prestador
  4. valor_total
  5. data_emissao

PRAZO:
  - Limite de 365 dias (1 ano) desde emissão
  - Reduz elegibilidade para planos com prazo curto

DOCUMENTO:
  Veja docs/caderno_projeto.md (R4 - Testes) para casos de teste
  Veja docs/planilha_testes_5_casos.md para resultados (Caso 4-5)

CONSTANTES:
  DEADLINE_DAYS = 365 (prazo limite)
  COMPLETENESS_FIELDS = campos validados
"""

from datetime import date
from pathlib import Path
from typing import Any, Dict, Iterable, Tuple

from .json_contracts import validar_contrato_json
from .reconciliation import load_claims, parse_date, reconcile


DEADLINE_DAYS = 30
COMPLETENESS_FIELDS = {
    "nome_profissional": "nome do profissional de saúde",
    "registro_profissional": "registro profissional",
    "descricao_servico": "descrição do serviço",
    "data_atendimento": "data do atendimento",
    "data_emissao": "data de emissão",
    "prestador": "prestador/estabelecimento",
    "valor_total": "valor da nota",
}


class ExportPeriodError(ValueError):
    """Raised when an export cannot establish which dates it covers."""


def validar_periodo_exportacao(
    exportacao: Dict[str, Any], nome_arquivo: str = "exportação"
) -> Tuple[date, date]:
    periodo = exportacao.get("periodo")
    if not isinstance(periodo, dict):
        raise ExportPeriodError(
            f"{nome_arquivo}: período ausente; informe as datas consultadas "
            "e importe novamente. Análise não executada."
        )

    inicio = parse_date(periodo.get("de") or periodo.get("inicio"))
    fim = parse_date(periodo.get("ate") or periodo.get("fim"))
    if inicio is None or fim is None:
        raise ExportPeriodError(
            f"{nome_arquivo}: período deve conter datas válidas em 'de' e 'ate'. "
            "Análise não executada."
        )
    if inicio > fim:
        raise ExportPeriodError(
            f"{nome_arquivo}: data inicial posterior à data final. "
            "Análise não executada."
        )
    if not isinstance(exportacao.get("reembolsos"), list):
        raise ExportPeriodError(
            f"{nome_arquivo}: lista 'reembolsos' ausente ou inválida. "
            "Análise não executada."
        )
    try:
        validar_contrato_json(
            exportacao,
            "plan_export.schema.json",
            nome_arquivo,
        )
    except ValueError as erro:
        raise ExportPeriodError(str(erro)) from erro
    return inicio, fim


def carregar_exportacao(caminho: Path) -> Dict[str, Any]:
    import json

    with caminho.open("r", encoding="utf-8") as arquivo:
        exportacao = json.load(arquivo)
    if not isinstance(exportacao, dict):
        raise ExportPeriodError(
            f"{caminho.name}: raiz JSON inválida; análise não executada."
        )
    validar_periodo_exportacao(exportacao, caminho.name)
    return exportacao


def avaliar_documento(
    documento: Dict[str, Any],
    exportacoes: Iterable[Dict[str, Any]],
    mapping: Dict[str, Any],
    data_referencia: date,
    dias_prazo: int = DEADLINE_DAYS,
) -> Dict[str, Any]:
    if dias_prazo < 0:
        raise ValueError("O prazo deve ser um número de dias não negativo.")

    exportacoes_lista = list(exportacoes)
    if not exportacoes_lista:
        raise ExportPeriodError(
            "Nenhuma exportação do plano selecionada; análise não executada."
        )

    periodos = [
        validar_periodo_exportacao(
            exportacao,
            str(exportacao.get("_nome_arquivo", f"exportação {index + 1}")),
        )
        for index, exportacao in enumerate(exportacoes_lista)
    ]

    data_atendimento = parse_date(documento.get("data_atendimento"))
    data_emissao = parse_date(documento.get("data_emissao"))
    data_prazo = data_atendimento or data_emissao
    origem_data_prazo = (
        "data_atendimento" if data_atendimento else "data_emissao" if data_emissao else None
    )

    if data_prazo is None:
        dias_desde_servico = None
        situacao_prazo = "indeterminado"
    else:
        dias_desde_servico = (data_referencia - data_prazo).days
        if dias_desde_servico < 0:
            situacao_prazo = "data_futura"
        elif dias_desde_servico > dias_prazo:
            situacao_prazo = "fora_do_prazo_simulado"
        else:
            situacao_prazo = "dentro_do_prazo_simulado"

    campos_ausentes = [
        descricao
        for campo, descricao in COMPLETENESS_FIELDS.items()
        if documento.get(campo) is None or documento.get(campo) == ""
    ]
    cobertura_periodo = (
        any(inicio <= data_prazo <= fim for inicio, fim in periodos)
        if data_prazo
        else None
    )
    erros_exportacao = [
        erro
        for exportacao in exportacoes_lista
        for erro in (exportacao.get("erros") or [])
    ]

    claims_by_id: Dict[str, Dict[str, Any]] = {}
    for exportacao in exportacoes_lista:
        for claim in load_claims(exportacao, mapping):
            claims_by_id[claim["source_id"]] = claim

    notas_normalizadas = [
        {
            "source_id": "documento_enviado",
            "filename": str(documento.get("_nome_arquivo", "documento.pdf")),
            "processed": True,
            "successful": True,
            "provider": documento.get("prestador"),
            "provider_tax_id": documento.get("cnpj_cpf_prestador"),
            "invoice_number": documento.get("numero_documento"),
            "amount": documento.get("valor_total"),
            "issue_date": documento.get("data_emissao"),
            "service_date": documento.get("data_atendimento"),
            "service": documento.get("descricao_servico"),
        }
    ]
    comparacao = reconcile(
        notas_normalizadas,
        list(claims_by_id.values()),
        mapping,
    )[0]
    candidatos = comparacao["candidates"]
    if candidatos:
        situacao_pedido = "localizado"
    elif erros_exportacao:
        situacao_pedido = "exportacao_com_erros"
    elif data_prazo is None:
        situacao_pedido = "data_documento_indeterminada"
    elif cobertura_periodo is not True:
        situacao_pedido = "periodo_nao_coberto"
    else:
        situacao_pedido = "nao_localizado_nas_exportacoes"

    return {
        "data_referencia": data_referencia.isoformat(),
        "prazo_simulado_dias": dias_prazo,
        "data_base_prazo": data_prazo.isoformat() if data_prazo else None,
        "origem_data_base_prazo": origem_data_prazo,
        "dias_desde_atendimento_ou_emissao": dias_desde_servico,
        "situacao_prazo": situacao_prazo,
        "situacao_pedido": situacao_pedido,
        "periodo_dos_datasets_cobre_data_base": cobertura_periodo,
        "periodos_exportados": [
            {"de": inicio.isoformat(), "ate": fim.isoformat()}
            for inicio, fim in periodos
        ],
        "campos_incompletos": campos_ausentes,
        "erros_exportacao": erros_exportacao,
        "candidatos": candidatos,
        "alternativas": comparacao["alternatives"],
        "aviso_prazo": (
            "Prazo de 30 dias é uma regra simulada para teste, não confirmação da "
            "regra contratual do plano."
        ),
    }
