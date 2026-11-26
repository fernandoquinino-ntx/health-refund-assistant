import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from .paths import resolve_schema


def _resolver_referencia_local(schema_raiz: dict[str, Any], referencia: str) -> Any:
    if not referencia.startswith("#/"):
        raise ValueError(
            f"Referência de schema não suportada para template: {referencia}"
        )

    valor: Any = schema_raiz
    for segmento in referencia[2:].split("/"):
        chave = segmento.replace("~1", "/").replace("~0", "~")
        if not isinstance(valor, dict) or chave not in valor:
            raise ValueError(f"Referência de schema não encontrada: {referencia}")
        valor = valor[chave]
    return valor


def _template_do_schema(
    schema: dict[str, Any],
    schema_raiz: dict[str, Any],
) -> Any:
    if "$ref" in schema:
        resolvido = _resolver_referencia_local(schema_raiz, schema["$ref"])
        if not isinstance(resolvido, dict):
            raise ValueError(f"Referência de schema não é um objeto: {schema['$ref']}")
        return _template_do_schema(resolvido, schema_raiz)

    opcoes = schema.get("anyOf") or schema.get("oneOf")
    if isinstance(opcoes, list) and opcoes:
        for opcao in opcoes:
            tipo = opcao.get("type") if isinstance(opcao, dict) else None
            if tipo == "null" or (
                isinstance(tipo, list) and "null" in tipo
            ):
                return None
        primeira_opcao = opcoes[0]
        if isinstance(primeira_opcao, dict):
            return _template_do_schema(primeira_opcao, schema_raiz)
        raise ValueError("Opção de schema inválida ao criar template JSON.")

    tipo = schema.get("type")
    if isinstance(tipo, list):
        if "null" in tipo:
            return None
        tipo = tipo[0] if tipo else None

    if tipo == "object":
        propriedades = schema.get("properties", {})
        obrigatorios = schema.get("required", propriedades.keys())
        return {
            nome: _template_do_schema(propriedades[nome], schema_raiz)
            for nome in obrigatorios
            if nome in propriedades
        }
    if tipo == "array":
        quantidade = schema.get("minItems", 0)
        item = schema.get("items", {})
        return [
            _template_do_schema(item, schema_raiz)
            for _ in range(quantidade)
        ]
    if tipo == "string":
        return schema.get("enum", ["<string>"])[0]
    if tipo == "number":
        return 0
    if tipo == "integer":
        return 0
    if tipo == "boolean":
        return False
    if tipo == "null":
        return None
    raise ValueError(f"Tipo de schema não suportado para template: {tipo!r}")


@lru_cache(maxsize=None)
def carregar_schema_json(nome_schema: str | Path) -> dict[str, Any]:
    caminho = nome_schema if isinstance(nome_schema, Path) else resolve_schema(nome_schema)
    with caminho.open("r", encoding="utf-8") as arquivo:
        schema = json.load(arquivo)
    if not isinstance(schema, dict):
        raise ValueError(f"O schema JSON precisa ser um objeto: {caminho}")
    Draft202012Validator.check_schema(schema)
    return schema


def contexto_schema_para_prompt(nome_schema: str) -> str:
    schema = carregar_schema_json(nome_schema)
    template = _template_do_schema(schema, schema)
    
    # Encontra o diretório relativo para documentação
    schema_path = resolve_schema(nome_schema)
    relative_path = schema_path.relative_to(resolve_schema(nome_schema).parents[2])
    
    return (
        f"Contrato carregado pela aplicação de `{relative_path}` "
        "(não dependa de acessar esse caminho):\n"
        "Schema JSON completo:\n"
        f"```json\n{json.dumps(schema, ensure_ascii=False, indent=2)}\n```\n"
        "Template JSON correspondente. Substitua os valores de exemplo pelos "
        "dados encontrados e preserve as chaves:\n"
        f"```json\n{json.dumps(template, ensure_ascii=False, indent=2)}\n```"
    )


@lru_cache(maxsize=None)
def _carregar_validador(nome_schema: str | Path) -> Draft202012Validator:
    schema = carregar_schema_json(nome_schema)
    return Draft202012Validator(schema)


def validar_contrato_json(
    dados: Any, nome_schema: str | Path, origem: str
) -> None:
    validador = _carregar_validador(nome_schema)
    erros = sorted(
        validador.iter_errors(dados),
        key=lambda erro: tuple(str(parte) for parte in erro.absolute_path),
    )
    if not erros:
        return

    erro = erros[0]
    caminho = ".".join(str(parte) for parte in erro.absolute_path) or "<raiz>"
    raise ValueError(
        f"{origem}: JSON incompatível com {nome_schema} em "
        f"{caminho}: {erro.message}"
    )
