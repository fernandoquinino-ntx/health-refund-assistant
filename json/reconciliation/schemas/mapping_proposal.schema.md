# `mapping_proposal.schema.json`

Contrato de saída JSON para o prompt
[`reembolso_status/v1.0.txt`](../../prompts/reembolso_status/v1.0.txt). O prompt
declara este schema antes de solicitar a resposta; `mapping.py` valida a proposta e
depois a mescla na configuração ativa, que é validada por
[`mapping_config.schema.json`](./mapping_config.schema.json).

Os caminhos sugeridos ainda são conferidos contra os campos disponíveis e precisam de
revisão humana antes de ativação.
