"""Tarefa de IA para estimar processamento e conferir seus cálculos."""

import json
from datetime import date, timedelta
from typing import Any

from ..plan.reconciliation import parse_date
from ..core.prompt_library import carregar_prompt
from .structured_ai import request_structured_json


AVISO = (
    "Estimativa de cinco dias úteis informada pelo usuário, não verificada junto "
    "à Care Plus e não é garantia de pagamento. Feriados não foram considerados. "
    "O status da exportação pode estar desatualizado; confira no portal."
)
STATUS_PERMITIDOS = {
    "em_analise",
    "liberado_integral_aguardando_pagamento",
    "liberado_parcial_aguardando_pagamento",
}


def _dias_uteis_entre(inicio: date, fim: date) -> int:
    total = max(0, (fim - inicio).days)
    weeks, remainder = divmod(total, 7)
    return weeks * 5 + sum(
        (inicio + timedelta(days=offset)).weekday() < 5
        for offset in range(1, remainder + 1)
    )


def estimar_pagamento(
    assessment: dict[str, Any], reference_date: date, prompt_version: str = "v1.0"
) -> dict[str, Any]:
    candidates = assessment.get("candidatos", [])
    motivo = None
    if assessment.get("erros_exportacao"):
        motivo = "A exportação contém erros de coleta."
    elif candidates and "ids_com_registros_conflitantes" not in assessment:
        motivo = "Análise anterior sem verificação de conflitos; reenvie o PDF e as exportações."
    elif len(candidates) != 1 or candidates[0].get("strong") is not True:
        motivo = "Não há um único pedido com correspondência forte."
    elif candidates[0].get("claim_number") in assessment.get("ids_com_registros_conflitantes", []):
        motivo = "Há registros conflitantes para o mesmo pedido."
    else:
        candidate = candidates[0]
        submission = parse_date(candidate.get("request_date"))
        if candidate.get("payment_date") or (candidate.get("paid_amount") or 0) > 0:
            motivo = "Há informação de pagamento; consulte o portal para confirmar."
        elif candidate.get("financial_status") not in STATUS_PERMITIDOS:
            motivo = "O status do pedido não permite estimar o pagamento."
        elif submission is None:
            motivo = "A data de submissão está ausente ou é inválida."
        elif submission > reference_date:
            motivo = "A data de submissão é posterior à data de referência."
    if motivo:
        return {
            "situacao": "nao_e_possivel_estimar",
            "motivo": motivo,
            "data_referencia": reference_date.isoformat(),
            "aviso": AVISO,
        }

    prazo = submission
    try:
        for _ in range(5):
            prazo += timedelta(days=1)
            while prazo.weekday() >= 5:
                prazo += timedelta(days=1)
    except OverflowError as error:
        raise ValueError("Não é possível calcular a data estimada fora do calendário suportado.") from error
    expected = {
        "data_submissao": submission.isoformat(),
        "data_referencia": reference_date.isoformat(),
        "data_estimada": prazo.isoformat(),
        "dias_uteis_restantes": _dias_uteis_entre(reference_date, prazo),
        "dias_uteis_atraso": _dias_uteis_entre(prazo, reference_date),
        "situacao": "prazo_ultrapassado" if reference_date > prazo else "dentro_do_prazo",
    }
    prompt, version = carregar_prompt("estimativa_pagamento", prompt_version)
    result = request_structured_json(
        prompt,
        json.dumps(
            {"data_submissao": submission.isoformat(), "data_referencia": reference_date.isoformat()},
            ensure_ascii=False,
        ),
        "payment_estimate.schema.json",
    )
    if result != expected:
        raise ValueError(
            "A estimativa da IA não corresponde à conferência dos dias úteis; "
            "a resposta não foi gerada."
        )
    return {**result, "versao_prompt": version, "aviso": AVISO}
