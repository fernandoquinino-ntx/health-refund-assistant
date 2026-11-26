# `mapeamento_reembolsos.json`

- **Tipo:** configuração versionada da aplicação.
- **Finalidade:** define caminhos dos campos de nota e de pedido, além de tolerâncias
  para gerar candidatos de conciliação.
- **Consumidores:** assistente, conciliador e ferramenta de proposta de mapeamento.
- **Contrato:** [mapping_config.schema.json](../reconciliation/schemas/mapping_config.schema.json).
- **Proposta por modelo:** prompt padrão [reembolso_status/v1.2.md](../../prompts/reembolso_status/v1.2.md);
  o arquivo de configuração existente registra a versão histórica que o originou;
  saída validada por [mapping_proposal.schema.json](../reconciliation/schemas/mapping_proposal.schema.json).
- **Privacidade:** não deve receber dados de beneficiários ou registros de sinistro.

Edite somente após revisar as estruturas das fontes. Propostas automáticas precisam de
revisão humana antes de substituir esta configuração.
