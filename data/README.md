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
| `treinamento/` | Dataset privado | PDFs fornecidos, páginas, anotações e exportações; veja o [guia de anotação atual](../docs/40_testing/04_anotacao_documentos.md) |
| `sinteticos/documentos/` | Fixtures de documentos | PDFs fictícios C01–C15; JSONs dos casos ficam em `json/tests/synthetic/` |

PDFs locais podem conter dados pessoais/de saúde e são ignorados pelo Git. A pasta
`data/sinteticos/documentos/` contém somente PDFs fictícios reproduzíveis.
As entradas e os dados derivados de treinamento devem permanecer em `data/treinamento/`;
essa pasta, assim como `data/pdf/`, `data/pages/`, `data/ocr/` e `data/dataset/`,
é ignorada pelo Git. Use `treinamento/entrada/` para PDFs e imagens JPG/PNG e
`treinamento/paginas/`, `treinamento/ocr/` e `treinamento/dataset/` para dados
derivados. O OCR a 300 DPI usa `treinamento/paginas/ocr_300dpi/` e mantém
diagnósticos privados em `treinamento/logs/`. Esses diretórios não são protegidos
contra acesso local ou backup.
Arquivos já rastreados, incluindo as fixtures PDF existentes, não deixam de ser
versionados por causa do `.gitignore`; confira `git status` e não use `git add -f`.
