# `mapeamento_reembolsos.json`

- **Tipo:** configuração versionada da aplicação.
- **Finalidade:** define caminhos dos campos de nota e de pedido, além de tolerâncias
  para gerar candidatos de conciliação.
- **Consumidores:** assistente, conciliador e ferramenta de proposta de mapeamento.
- **Contrato:** [mapping_config.schema.json](../schemas/mapping_config.schema.json).
- **Proposta por modelo:** prompt [reembolso_status/v1.0.txt](../../prompts/reembolso_status/v1.0.txt);
  saída validada por [mapping_proposal.schema.json](../schemas/mapping_proposal.schema.json).
- **Privacidade:** não deve receber dados de beneficiários ou registros de sinistro.

Edite somente após revisar as estruturas das fontes. Propostas automáticas precisam de
revisão humana antes de substituir esta configuração.
