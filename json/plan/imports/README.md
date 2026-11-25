# Exportações importadas do plano

Este diretório contém **datasets de entrada** exportados pela extensão do portal e
importados pela aplicação. Cada arquivo preserva uma consulta e seu período; a
interface salva uma cópia com prefixo de data/hora para manter as importações
separadas.

- Formato: JSON com `periodo` e a lista `reembolsos`.
- Contrato: [`plan_export.schema.json`](../schemas/plan_export.schema.json).
- Leitura: `plan_exports.py` valida e lista os arquivos; `assessment.py` verifica se
  o período informado cobre a data do documento.
- Privacidade: exportações reais podem conter nomes, sinistros e dados de saúde.
  Esta pasta é local/ignorada pelo Git; não compartilhe nem versiona esses arquivos.

O arquivo baixado pela extensão não é alterado. A importação da interface cria a cópia
usada pelo assistente. Consulte o guia do tipo
[`*.json`](./exportacao_plano.md); não é criado um `.md` separado para cada exportação
individual.
