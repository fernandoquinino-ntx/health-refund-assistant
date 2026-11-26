# Documentos PDF locais e sintéticos

Esta pasta é destinada aos PDFs de entrada/saída e aos documentos sintéticos. Os JSONs
da aplicação foram centralizados em [`json/`](../json/); consulte o
[catálogo JSON](../docs/70_documentation/05_json_catalogo.md) para localizar datasets, estado, relatórios,
configuração e schemas.

| Pasta | Tipo | O que armazena |
|---|---|---|
| `incoming/` | Entrada de documentos | PDFs aguardando análise/processamento |
| `processed/` | Arquivo operacional | PDFs processados e duplicatas |
| `failed/` | Fila de revisão | PDFs que falharam e podem ser reprocessados |
| `sinteticos/documentos/` | Fixtures de documentos | PDFs fictícios C01–C15; JSONs dos casos ficam em `json/tests/synthetic/` |

PDFs locais podem conter dados pessoais/de saúde e são ignorados pelo Git. A pasta
`data/sinteticos/documentos/` contém somente PDFs fictícios reproduzíveis.
