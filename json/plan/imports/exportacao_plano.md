# Tipo `json/plan/imports/*.json`

Cada arquivo JSON nesta pasta é uma cópia de uma exportação do portal importada pela
interface. A cópia recebe prefixo de data/hora para manter versões distintas; o
original baixado pela extensão permanece em Downloads.

- **Usado por:** assistente e conciliador como fonte de pedidos/status exportados.
- **Contrato:** [plan_export.schema.json](../schemas/plan_export.schema.json).
- **Privacidade:** pode conter nomes, beneficiários, sinistros e dados de saúde; não
  versionar nem compartilhar.

Este guia vale para cada exportação. Não crie documentação separada para cada arquivo
baixado.
