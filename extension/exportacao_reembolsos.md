# Exportação JSON de reembolsos

A extensão salva a exportação do portal na pasta Downloads do usuário. O nome segue o
padrão `careplus-reembolsos-AAAAMMDD-HHMM.json`; esse arquivo não é gravado
automaticamente dentro do repositório.

Ao enviar o arquivo na interface Streamlit, a aplicação valida o período e grava uma
cópia com prefixo de data/hora em `json/plan/imports/`.

- **Contrato:** [plan_export.schema.json](../json/schemas/plan_export.schema.json).
- **Privacidade:** contém dados pessoais e de saúde; não versionar nem compartilhar.
- **Campos:** consulte [LEIAME.md](./LEIAME.md).
