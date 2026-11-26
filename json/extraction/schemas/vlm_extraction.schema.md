# `vlm_extraction.schema.json`

Contrato JSON Schema Draft 2020-12 usado pela API OpenAI para validar a saída dos
prompts [v1.0](../../../prompts/vlm_extractor/v1.0.md),
[v1.1](../../../prompts/vlm_extractor/v1.1.md),
[v2.0](../../../prompts/vlm_extractor/v2.0.md) e
[v3.0](../../../prompts/vlm_extractor/v3.0.md).

Cada prompt declara este caminho como seu contrato de saída. O contrato contém nove
campos; o código também valida respostas caso o endpoint não suporte `json_schema`.
