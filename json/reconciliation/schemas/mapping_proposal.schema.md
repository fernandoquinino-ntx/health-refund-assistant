# `mapping_proposal.schema.json`

Contrato de saída JSON para os prompts
[`reembolso_status/v1.0.md`](../../../prompts/reembolso_status/v1.0.md) e
[`reembolso_status/v1.1.md`](../../../prompts/reembolso_status/v1.1.md). O código
envia este schema antes de solicitar a resposta; `mapping.py` valida a proposta e
depois a mescla a uma cópia da configuração ativa para revisão, validada por
[`mapping_config.schema.json`](./mapping_config.schema.json).

Os caminhos sugeridos ainda são conferidos contra os campos disponíveis e precisam de
revisão humana antes de ativação.
