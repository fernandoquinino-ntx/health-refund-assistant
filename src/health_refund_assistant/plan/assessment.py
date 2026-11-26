"""Objetivo: avaliar campos e possíveis pedidos nas exportações do plano.

Entradas: dados extraídos, exportações, mapeamento e data de referência.
Processamento: verifica campos, cobertura, candidatos e prazo simulado.
Saídas: evidências estruturadas; não determina elegibilidade contratual.
"""

from datetime import date, timedelta
import json
from pathlib import Path
from typing import Any, Dict, Iterable, Tuple

from ..core.json_contracts import validar_contrato_json
from ..core.paths import PRAZO_CONFIG_PATH
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


def carregar_regras_prazo_confirmadas() -> Dict[str, Any]:
    """Carrega regras contratuais opcionais; sem confirmação todas ficam desativadas."""
    if not PRAZO_CONFIG_PATH.exists():
        return {
            "regras_confirmadas": False,
            "d2": {"ativo": False, "dias": 2},
            "365": {"ativo": False, "dias": 365},
        }
    try:
        config = json.loads(PRAZO_CONFIG_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError("O arquivo de regras de prazo é inválido.") from error
    if not isinstance(config, dict):
        raise ValueError("O arquivo de regras de prazo deve ser um objeto JSON.")
    if config.get("regras_confirmadas") is not True:
        return {
            "regras_confirmadas": False,
            "d2": {"ativo": False, "dias": 2},
            "365": {"ativo": False, "dias": 365},
        }
    d2 = config.get("d2") if isinstance(config.get("d2"), dict) else {}
    prazo_365 = config.get("365") if isinstance(config.get("365"), dict) else {}
    return {
        "regras_confirmadas": True,
        "d2": {"ativo": d2.get("ativo") is True, "dias": d2.get("dias", 2)},
        "365": {"ativo": prazo_365.get("ativo") is True, "dias": prazo_365.get("dias", 365)},
    }


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

    claims_by_id: Dict[str, list[Dict[str, Any]]] = {}
    for exportacao in exportacoes_lista:
        for claim in load_claims(exportacao, mapping):
            versions = claims_by_id.setdefault(claim["source_id"], [])
            if claim not in versions:
                versions.append(claim)

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
        [claim for versions in claims_by_id.values() for claim in versions],
        mapping,
    )[0]
    candidatos = comparacao["candidates"]
    if candidatos:
        situacao_pedido = "localizado"
        data_prazo = None
        origem_data_prazo = None
        dias_desde_servico = None
        situacao_prazo = "nao_aplicavel_pedido_localizado"
    elif erros_exportacao:
        situacao_pedido = "exportacao_com_erros"
    elif data_prazo is None:
        situacao_pedido = "data_documento_indeterminada"
    elif cobertura_periodo is not True:
        situacao_pedido = "periodo_nao_coberto"
    else:
        situacao_pedido = "nao_localizado_nas_exportacoes"

    if not candidatos:
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

    regras_prazo = carregar_regras_prazo_confirmadas()
    datas_importacao = [
        parse_date(
            exportacao.get("importado_em")[:10]
            if isinstance(exportacao.get("importado_em"), str)
            else exportacao.get("_importado_em")
        )
        for exportacao in exportacoes_lista
    ]
    datas_importacao_validas = [valor for valor in datas_importacao if valor is not None]
    data_importacao = max(datas_importacao_validas) if datas_importacao_validas else data_referencia

    d2 = {
        "ativo": False,
        "situacao": "desativado",
        "aviso": "A regra D-2 não está confirmada; não use esta informação como regra do plano.",
    }
    if (
        regras_prazo["regras_confirmadas"]
        and regras_prazo["d2"]["ativo"]
        and periodos
    ):
        dias_d2 = int(regras_prazo["d2"]["dias"])
        corte_d2 = data_importacao - timedelta(days=dias_d2)
        if candidatos:
            situacao_d2 = "pedido_localizado"
        elif data_prazo is None:
            situacao_d2 = "data_documento_indeterminada"
        elif data_prazo > corte_d2:
            situacao_d2 = "aguardando_completude_d2"
        elif cobertura_periodo is not True:
            situacao_d2 = "exportacao_nao_cobre_documento"
        else:
            situacao_d2 = "ausencia_confirmada_na_exportacao"
        d2 = {
            "ativo": True,
            "dias": dias_d2,
            "corte_exportacao": corte_d2.isoformat(),
            "data_importacao": data_importacao.isoformat(),
            "situacao": situacao_d2,
            "aviso": (
                "D-2 confirmado: documentos desta data ou anteriores podem ser "
                "considerados ausentes somente quando cobertos pelo período exportado."
            ),
        }

    prazo_365 = {
        "ativo": False,
        "situacao": "desativado",
        "aviso": "A regra de 365 dias não está confirmada; não use esta informação como elegibilidade.",
    }
    if (
        regras_prazo["regras_confirmadas"]
        and regras_prazo["365"]["ativo"]
        and data_prazo is not None
    ):
        dias_365 = int(regras_prazo["365"]["dias"])
        prazo_final = data_prazo + timedelta(days=dias_365)
        dias_restantes = (prazo_final - data_referencia).days
        if candidatos:
            situacao_365 = "pedido_localizado_regra_nao_bloqueia"
        elif dias_restantes < 0:
            situacao_365 = "prazo_expirado_sem_pedido"
        else:
            situacao_365 = "dentro_do_prazo_para_novo_pedido"
        prazo_365 = {
            "ativo": True,
            "dias": dias_365,
            "prazo_final": prazo_final.isoformat(),
            "dias_restantes": max(dias_restantes, 0),
            "situacao": situacao_365,
            "aviso": "Prazo de 365 dias baseado na configuração contratual confirmada.",
        }

    return {
        "data_referencia": data_referencia.isoformat(),
        "regras_prazo_confirmadas": regras_prazo["regras_confirmadas"],
        "corte_d2": d2,
        "prazo_365": prazo_365,
        "pode_abrir_novo_pedido": (
            False
            if prazo_365["situacao"] == "prazo_expirado_sem_pedido"
            else None
        ),
        "prazo_simulado_dias": dias_prazo if not candidatos else None,
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
        "ids_com_registros_conflitantes": [
            claim_id for claim_id, versions in claims_by_id.items() if len(versions) > 1
        ],
        "candidatos": candidatos,
        "alternativas": comparacao["alternatives"],
        "aviso_prazo": (
            f"Prazo de {dias_prazo} dias é uma regra simulada para teste, não confirmação da "
            "regra contratual do plano."
        ) if not candidatos else "Prazo de envio não analisado para pedido localizado.",
    }
