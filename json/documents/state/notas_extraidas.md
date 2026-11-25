# `notas_extraidas.json`

Arquivo de estado operacional gravado pelo processamento em lote em
`json/documents/state/notas_extraidas.json`.

Registra o resultado extraído de cada nota, caminho e hash do PDF, modelo/versão de
prompt e possíveis duplicatas. É consumido pela conciliação e por ferramentas de
revisão.

- **Contrato:** [notes_state.schema.json](../schemas/notes_state.schema.json).
- **Privacidade:** pode conter dados pessoais/de saúde; fica local e não deve ser
  versionado.
- **Diferença:** a análise de um PDF enviado diretamente pelo navegador não persiste
  sua extração neste arquivo.
