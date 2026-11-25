# Relatórios locais

Esta pasta é um índice das saídas derivadas, não o local dos arquivos. São regeneráveis
e ignorados pelo Git; ficam separados pelo processo:

| Arquivo | Tipo e finalidade | Schema | Guia |
|---|---|---|---|
| `evaluation/reports/*.json` | Métricas observadas de uma execução do benchmark VLM | [`vlm_evaluation_report.schema.json`](../schemas/vlm_evaluation_report.schema.json) | [`avaliacao.md`](../evaluation/reports/avaliacao.md) |
| `reconciliation/reports/*.json` | Candidatos e evidências da conciliação de notas com a exportação | [`reconciliation_report.schema.json`](../schemas/reconciliation_report.schema.json) | [`conciliacao.md`](../reconciliation/reports/conciliacao.md) |

Relatórios podem repetir dados pessoais presentes nas entradas. Compartilhe apenas
relatórios produzidos com fixtures sintéticas.
