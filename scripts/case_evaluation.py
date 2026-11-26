"""Executa a avaliação de extração do VLM contra casos e gabaritos sintéticos."""

import argparse
import json
import math
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from health_refund_assistant.documents.pdf_converter import converter_primeira_pagina_pdf_base64
from health_refund_assistant.core.json_contracts import validar_contrato_json
from health_refund_assistant.documents.vlm_extractor import (
    DEFAULT_MODEL,
    EXTRACTION_FIELDS as EXTRACTION_FIELDS_V3,
    EXTRACTION_FIELDS_V4,
    VERSOES_SCHEMA_V4,
    VLMExtractor,
)

if __package__:
    from .test_paths import EVALUATION_REPORTS_DIR, SYNTHETIC_DATA_DIR, SYNTHETIC_DOCUMENTS_DIR, TEST_SCHEMAS
else:
    from test_paths import EVALUATION_REPORTS_DIR, SYNTHETIC_DATA_DIR, SYNTHETIC_DOCUMENTS_DIR, TEST_SCHEMAS


DEFAULT_CASES = SYNTHETIC_DATA_DIR / "casos_teste.json"
DEFAULT_GOLD = SYNTHETIC_DATA_DIR / "gabarito.json"
DEFAULT_DOCUMENTS = SYNTHETIC_DOCUMENTS_DIR
DEFAULT_REPORT = EVALUATION_REPORTS_DIR / "avaliacao.json"
MINIMUM_CASES = 15
EXTRACTION_FIELDS = set(EXTRACTION_FIELDS_V4)
STRING_FIELDS = EXTRACTION_FIELDS - {"valor_total", "imagem_legivel"}


def carregar_json(caminho: Path) -> Dict[str, Any]:
    with caminho.open("r", encoding="utf-8") as arquivo:
        dados = json.load(arquivo)
    if not isinstance(dados, dict):
        raise ValueError(f"O arquivo deve conter um objeto JSON: {caminho}")
    return dados


def comparar_valor(
    campo: str, esperado: Any, obtido: Any, tolerancia_valor: float
) -> bool:
    if campo == "valor_total":
        if esperado is None:
            return obtido is None
        if (
            isinstance(esperado, bool)
            or not isinstance(esperado, (int, float))
            or isinstance(obtido, bool)
            or not isinstance(obtido, (int, float))
        ):
            return False
        try:
            esperado_decimal = Decimal(str(esperado))
            obtido_decimal = Decimal(str(obtido))
            tolerancia_decimal = Decimal(str(tolerancia_valor))
        except InvalidOperation:
            return False
        return (
            esperado_decimal.is_finite()
            and obtido_decimal.is_finite()
            and abs(esperado_decimal - obtido_decimal) <= tolerancia_decimal
        )

    if esperado is None:
        return obtido is None
    if isinstance(esperado, bool):
        return isinstance(obtido, bool) and obtido is esperado
    if isinstance(esperado, (int, float)):
        return (
            not isinstance(obtido, bool)
            and isinstance(obtido, (int, float))
            and obtido == esperado
        )
    return type(obtido) is type(esperado) and obtido == esperado


def comparar_campos(
    esperados: Dict[str, Any],
    obtidos: Dict[str, Any],
    tolerancia_valor: float,
) -> Dict[str, Dict[str, Any]]:
    resultados = {}
    for campo, esperado in esperados.items():
        resultados[campo] = {
            "passou": comparar_valor(
                campo, esperado, obtidos.get(campo), tolerancia_valor
            ),
            "esperado": esperado,
            "obtido": obtidos.get(campo),
        }
    return resultados


def _validar_tipo_esperado(campo: str, esperado: Any, caso_id: str) -> None:
    if campo == "valor_total":
        valido = (
            esperado is None
            or (
                isinstance(esperado, (int, float))
                and not isinstance(esperado, bool)
                and math.isfinite(float(esperado))
            )
        )
    elif campo == "imagem_legivel":
        valido = isinstance(esperado, bool)
    elif campo in STRING_FIELDS:
        valido = esperado is None or isinstance(esperado, str)
    else:
        valido = False
    if not valido:
        raise ValueError(
            f"Tipo de valor inválido no gabarito: {caso_id}.{campo}"
        )


def _validar_manifesto(
    casos_documento: Dict[str, Any], gabarito_documento: Dict[str, Any]
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    if casos_documento.get("schema_version") == 2:
        validar_contrato_json(
            casos_documento,
            TEST_SCHEMAS["test_cases.schema.json"],
            "manifesto de casos",
        )
    if gabarito_documento.get("schema_version") == 2:
        validar_contrato_json(
            gabarito_documento,
            TEST_SCHEMAS["test_gold.schema.json"],
            "gabarito de casos",
        )

    casos = casos_documento.get("casos")
    gabarito = gabarito_documento.get("casos")
    if not isinstance(casos, list):
        raise ValueError("O manifesto deve conter 'casos' como uma lista.")
    if not isinstance(gabarito, dict):
        raise ValueError("O gabarito deve conter 'casos' como um objeto.")

    ids = []
    executaveis = []
    for caso in casos:
        if not isinstance(caso, dict):
            raise ValueError("Cada caso do manifesto deve ser um objeto.")
        caso_id = caso.get("id")
        if not isinstance(caso_id, str) or not caso_id.strip():
            raise ValueError("Cada caso precisa de um 'id' não vazio.")
        ids.append(caso_id)
        if not isinstance(caso.get("falha_critica", False), bool):
            raise ValueError(
                f"'falha_critica' deve ser booleano no caso {caso_id}."
            )

        executar = caso.get("executar_vlm")
        if not isinstance(executar, bool):
            raise ValueError(
                f"O caso {caso_id} precisa declarar 'executar_vlm' como booleano."
            )
        if not executar:
            continue

        if not isinstance(caso.get("arquivo"), str) or not caso["arquivo"]:
            raise ValueError(f"O caso executável {caso_id} precisa de um PDF.")
        entrada_gabarito = gabarito.get(caso_id)
        if not isinstance(entrada_gabarito, dict):
            raise ValueError(f"Falta o caso {caso_id} no gabarito.")
        campos = entrada_gabarito.get("campos")
        if not isinstance(campos, dict) or not campos:
            raise ValueError(
                f"O gabarito do caso {caso_id} precisa ter ao menos um campo esperado."
            )
        campos_desconhecidos = set(campos) - EXTRACTION_FIELDS
        if campos_desconhecidos:
            raise ValueError(
                f"Campos não extraídos pelo VLM no caso {caso_id}: "
                f"{', '.join(sorted(campos_desconhecidos))}"
            )
        for campo, esperado in campos.items():
            _validar_tipo_esperado(campo, esperado, caso_id)
        executaveis.append(caso)

    if len(ids) != len(set(ids)):
        raise ValueError("Os IDs dos casos precisam ser únicos.")
    ids_desconhecidos = set(gabarito) - set(ids)
    if ids_desconhecidos:
        raise ValueError(
            "O gabarito contém IDs ausentes do manifesto: "
            + ", ".join(sorted(ids_desconhecidos))
        )
    return executaveis, gabarito


def _caminho_pdf_seguro(pasta_documentos: Path, arquivo: str) -> Path:
    raiz = pasta_documentos.resolve()
    caminho = (raiz / arquivo).resolve()
    if not caminho.is_relative_to(raiz):
        raise ValueError(f"O caminho do caso sai da pasta de documentos: {arquivo}")
    if caminho.suffix.lower() != ".pdf":
        raise ValueError(f"O documento do caso precisa ser PDF: {arquivo}")
    if not caminho.is_file():
        raise FileNotFoundError(f"PDF do caso não encontrado: {caminho}")
    return caminho


def executar_avaliacao(
    caminho_casos: Path,
    caminho_gabarito: Path,
    pasta_documentos: Path,
    caminho_relatorio: Path,
    model: str = DEFAULT_MODEL,
    prompt_version: Optional[str] = None,
    tolerancia_valor: float = 0.01,
    acuracia_minima: float = 0.85,
) -> Dict[str, Any]:
    if not 0 <= acuracia_minima <= 1:
        raise ValueError("A acurácia mínima deve estar entre 0 e 1.")
    if not math.isfinite(tolerancia_valor) or tolerancia_valor < 0:
        raise ValueError("A tolerância monetária deve ser um número finito não negativo.")

    casos_documento = carregar_json(caminho_casos)
    gabarito_documento = carregar_json(caminho_gabarito)
    casos_executaveis, gabarito = _validar_manifesto(
        casos_documento, gabarito_documento
    )
    if not casos_executaveis:
        raise ValueError("Não há casos de extração marcados para execução.")

    documentos = {
        caso["id"]: _caminho_pdf_seguro(pasta_documentos, caso["arquivo"])
        for caso in casos_executaveis
    }
    extrator = VLMExtractor(model=model, prompt_version=prompt_version)
    resultados = []

    for caso in casos_documento["casos"]:
        caso_id = caso["id"]
        if not caso["executar_vlm"]:
            resultados.append(
                {
                    "caso_id": caso_id,
                    "estado": "fora_do_escopo_atual",
                    "motivo": caso.get(
                        "motivo_fora_escopo",
                        "Este caso depende de comportamento ainda não implementado.",
                    ),
                }
            )
            continue

        try:
            imagem = converter_primeira_pagina_pdf_base64(
                str(documentos[caso_id])
            )
            obtido = extrator.extrair_dados_nf_visual(imagem)
            meta = obtido.get("_meta", {})
            esperado = gabarito[caso_id]["campos"]
            if extrator.prompt_version not in VERSOES_SCHEMA_V4:
                esperado = {
                    campo: valor
                    for campo, valor in esperado.items()
                    if campo in EXTRACTION_FIELDS_V3
                }
            comparacao = comparar_campos(
                esperado, obtido, tolerancia_valor
            )
            passou = (
                meta.get("status") == "OK"
                and all(item["passou"] for item in comparacao.values())
            )
            resultados.append(
                {
                    "caso_id": caso_id,
                    "estado": "passou" if passou else "falhou",
                    "falha_critica": bool(caso.get("falha_critica"))
                    and not passou,
                    "status_extracao": meta.get("status"),
                    "campos": comparacao,
                }
            )
        except Exception as erro:
            resultados.append(
                {
                    "caso_id": caso_id,
                    "estado": "erro",
                    "falha_critica": bool(caso.get("falha_critica")),
                    "erro_tipo": type(erro).__name__,
                }
            )

    executados = [
        resultado
        for resultado in resultados
        if resultado["estado"] in {"passou", "falhou", "erro"}
    ]
    comparacoes = [
        campo
        for resultado in executados
        for campo in resultado.get("campos", {}).values()
    ]
    campos_corretos = sum(campo["passou"] for campo in comparacoes)
    acuracia_campos = (
        campos_corretos / len(comparacoes) if comparacoes else 0.0
    )
    casos_corretos = sum(
        resultado["estado"] == "passou" for resultado in executados
    )
    acuracia_casos = (
        casos_corretos / len(executados) if executados else 0.0
    )
    respostas_ok = sum(
        resultado.get("status_extracao") == "OK" for resultado in executados
    )
    taxa_respostas_ok = respostas_ok / len(executados) if executados else 0.0
    falhas_criticas = sum(
        bool(resultado.get("falha_critica")) for resultado in resultados
    )
    suite_completa = (
        len(casos_documento["casos"]) >= MINIMUM_CASES
        and len(executados) == len(casos_documento["casos"])
    )
    aprovado = (
        suite_completa
        and acuracia_casos >= acuracia_minima
        and falhas_criticas == 0
    )

    relatorio = {
        "schema_version": 1,
        "executado_em": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "model": extrator.model,
        "prompt_version": extrator.prompt_version,
        "tolerancia_valor": tolerancia_valor,
        "acuracia_minima_proposta": acuracia_minima,
        "resumo": {
            "casos_no_manifesto": len(casos_documento["casos"]),
            "casos_executados": len(executados),
            "casos_fora_do_escopo": sum(
                resultado["estado"] == "fora_do_escopo_atual"
                for resultado in resultados
            ),
            "campos_corretos": campos_corretos,
            "campos_comparados": len(comparacoes),
            "acuracia_por_campo": round(acuracia_campos, 4),
            "respostas_com_status_ok": respostas_ok,
            "respostas_avaliadas": len(executados),
            "taxa_respostas_ok": round(taxa_respostas_ok, 4),
            "casos_corretos": casos_corretos,
            "acuracia_por_caso": round(acuracia_casos, 4),
            "falhas_criticas": falhas_criticas,
            "suite_completa": suite_completa,
            "aprovado": aprovado,
        },
        "resultados": resultados,
    }
    validar_contrato_json(
        relatorio,
        TEST_SCHEMAS["vlm_evaluation_report.schema.json"],
        caminho_relatorio.name,
    )

    caminho_relatorio.parent.mkdir(parents=True, exist_ok=True)
    temporario = caminho_relatorio.with_suffix(caminho_relatorio.suffix + ".tmp")
    temporario.write_text(
        json.dumps(relatorio, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temporario.replace(caminho_relatorio)
    return relatorio


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Avalia a extração do VLM contra um gabarito JSON separado."
    )
    parser.add_argument("--casos", type=Path, default=DEFAULT_CASES)
    parser.add_argument("--gabarito", type=Path, default=DEFAULT_GOLD)
    parser.add_argument("--documentos", type=Path, default=DEFAULT_DOCUMENTS)
    parser.add_argument("--saida", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--prompt-version")
    parser.add_argument("--tolerancia-valor", type=float, default=0.01)
    parser.add_argument("--acuracia-minima", type=float, default=0.85)
    args = parser.parse_args()

    try:
        relatorio = executar_avaliacao(
            caminho_casos=args.casos,
            caminho_gabarito=args.gabarito,
            pasta_documentos=args.documentos,
            caminho_relatorio=args.saida,
            model=args.model,
            prompt_version=args.prompt_version,
            tolerancia_valor=args.tolerancia_valor,
            acuracia_minima=args.acuracia_minima,
        )
    except (OSError, ValueError, json.JSONDecodeError) as erro:
        parser.error(str(erro))

    resumo = relatorio["resumo"]
    print(
        f"Casos: {resumo['casos_executados']}/"
        f"{resumo['casos_no_manifesto']} executados; "
        f"{resumo['casos_fora_do_escopo']} fora do escopo."
    )
    print(
        f"Acurácia por caso: {resumo['acuracia_por_caso']:.1%}; "
        f"falhas críticas: {resumo['falhas_criticas']}."
    )
    print(
        "Resultado: "
        + ("APROVADO" if resumo["aprovado"] else "INCOMPLETO/REPROVADO")
    )
    print(f"Relatório JSON: {args.saida}")
    if not resumo["aprovado"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
