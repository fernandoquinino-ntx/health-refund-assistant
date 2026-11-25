# `vlm_extraction.schema.json`

Contrato JSON Schema Draft 2020-12 usado pela API OpenAI para validar a saída dos
prompts [v1.0](../../prompts/vlm_extractor/v1.0.txt),
[v1.1](../../prompts/vlm_extractor/v1.1.txt),
[v2.0](../../prompts/vlm_extractor/v2.0.txt) e
[v3.0](../../prompts/vlm_extractor/v3.0.txt).

Cada prompt declara este caminho como seu contrato de saída. O contrato contém nove
campos; o código também valida respostas caso o endpoint não suporte `json_schema`.
