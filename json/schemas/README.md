# Contratos JSON

Os arquivos `*.schema.json` descrevem a forma e os tipos aceitos pelos JSONs
persistidos pelo projeto e saídas estruturadas de prompts. Eles usam JSON Schema
Draft 2020-12 e são usados na validação local e nas chamadas que aceitam `json_schema`.

| Schema | Tipo de JSON validado | Local do dado | Documentação |
|---|---|---|---|
| [plan_export.schema.json](./plan_export.schema.json) | Dataset de solicitações exportadas do plano | `json/plan/imports/` e `json/tests/synthetic/exportacao_ficticia.json` | [Descrição](./plan_export.schema.md) |
| [mapping_config.schema.json](./mapping_config.schema.json) | Configuração do mapeamento entre campos | `json/config/mapeamento_reembolsos.json` | [Descrição e prompt relacionado](./mapping_config.schema.md) |
| [notes_state.schema.json](./notes_state.schema.json) | Índice/estado do processamento local de PDFs | `json/documents/state/notas_extraidas.json` | [Descrição](./notes_state.schema.md) |
| [test_cases.schema.json](./test_cases.schema.json) | Manifesto de entradas dos casos de teste | `json/tests/templates/` e `json/tests/synthetic/` | [Descrição](./test_cases.schema.md) |
| [test_gold.schema.json](./test_gold.schema.json) | Gabarito isolado das entradas do modelo | `json/tests/templates/` e `json/tests/synthetic/` | [Descrição](./test_gold.schema.md) |
| [vlm_evaluation_report.schema.json](./vlm_evaluation_report.schema.json) | Resultado da avaliação de uma versão de prompt | `json/evaluation/reports/` | [Descrição](./vlm_evaluation_report.schema.md) |
| [reconciliation_report.schema.json](./reconciliation_report.schema.json) | Resultado da conciliação de notas e pedidos | `json/reconciliation/reports/` | [Descrição](./reconciliation_report.schema.md) |
| [vlm_extraction.schema.json](./vlm_extraction.schema.json) | Saída do extrator v1.0–v3.0 | API OpenAI | [Descrição e prompts](./vlm_extraction.schema.md) |
| [vlm_extraction_v4.schema.json](./vlm_extraction_v4.schema.json) | Saída do extrator v4.0 | API OpenAI | [Descrição e prompt](./vlm_extraction_v4.schema.md) |
| [mapping_proposal.schema.json](./mapping_proposal.schema.json) | Saída JSON do prompt de proposta de mapeamento | `mapping.py` antes da validação da configuração | [Descrição e prompt](./mapping_proposal.schema.md) |

O manifesto e o gabarito são contratos diferentes: o primeiro contém apenas dados de
entrada e perguntas; o segundo contém os valores esperados e nunca é enviado ao
prompt. Os dados importados e saídas locais podem conter informações pessoais; os
schemas documentam a estrutura, não tornam esses dados seguros para versionamento.

Os JSONs [`.devcontainer/devcontainer.json`](../../.devcontainer/devcontainer.json) e
[`extension/manifest.json`](../../extension/manifest.json) seguem contratos externos do
Dev Containers e do Chrome Manifest V3; não são datasets da aplicação.
