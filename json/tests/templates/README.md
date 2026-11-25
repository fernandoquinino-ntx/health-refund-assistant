# Templates JSON de teste

Estes arquivos são **templates-fonte versionados** usados pelo gerador de fixtures;
não são exportações importadas nem saídas de execução.

| Arquivo | Tipo | Conteúdo | Schema | Guia |
|---|---|---|---|---|
| `casos_teste.template.json` | Manifesto de teste | Documentos, perguntas, categorias e datas de referência | [`test_cases.schema.json`](../schemas/test_cases.schema.json) | [`casos_teste.template.md`](./casos_teste.template.md) |
| `gabarito.template.json` | Ground truth | Extração correta e avaliação determinística esperada para cada ID | [`test_gold.schema.json`](../schemas/test_gold.schema.json) | [`gabarito.template.md`](./gabarito.template.md) |

O gerador cria cópias executáveis em `json/tests/synthetic/`. Mantenha o gabarito separado
do manifesto e nunca o inclua no prompt enviado ao modelo.
