"""Executa tarefas de IA com schema estrito e validação local."""

import json
import os
from typing import Any

from openai import OpenAI

from ..documents.vlm_extractor import DEFAULT_MODEL, DEFAULT_OPENAI_BASE_URL, OPENAI_BASE_URL_ENV, OPENAI_TOKEN_ENV
from ..json_contracts import carregar_schema_json, validar_contrato_json


def request_structured_json(
    prompt: str, content: Any, schema_name: str
) -> dict[str, Any]:
    token = os.getenv(OPENAI_TOKEN_ENV)
    if not token:
        raise ValueError(f"Configure {OPENAI_TOKEN_ENV} antes de usar a IA.")
    schema = carregar_schema_json(schema_name)
    api_schema = {
        key: schema[key]
        for key in ("type", "properties", "required", "additionalProperties")
    }
    client = OpenAI(
        api_key=token,
        base_url=os.getenv(OPENAI_BASE_URL_ENV) or DEFAULT_OPENAI_BASE_URL,
        timeout=120.0,
    )
    response = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": content},
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": schema_name.split(".")[0],
                "strict": True,
                "schema": api_schema,
            },
        },
        max_completion_tokens=1200,
        reasoning_effort="none",
    )
    if not response.choices or not response.choices[0].message.content:
        raise ValueError("A IA não retornou uma resposta utilizável; tarefa não concluída.")
    try:
        result = json.loads(response.choices[0].message.content)
    except json.JSONDecodeError as error:
        raise ValueError("A IA retornou JSON inválido; tarefa não concluída.") from error
    validar_contrato_json(result, schema_name, "resposta da IA")
    return result
