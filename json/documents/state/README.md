# Estado local

## `notas_extraidas.json`

Este arquivo pode conter nomes, identificadores e dados de saúde extraídos. É local e
ignorado pelo Git. Consulte a [documentação por tipo](./notas_extraidas.md) e o
[schema](../schemas/notes_state.schema.json). Não o use como gabarito e não o copie
para `json/tests/synthetic/`.

## `conversa_local.json`

Memória persistente de uso individual: últimas 50 mensagens e evidências da última
análise. É ignorada pelo Git, não é criptografada e pode conter dados de saúde.
O PDF não é armazenado nesse arquivo. A interface oferece a exclusão da conversa;
exportações importadas e dados enviados à API não são removidos por essa ação.
Não há autenticação nem isolamento entre usuários.
