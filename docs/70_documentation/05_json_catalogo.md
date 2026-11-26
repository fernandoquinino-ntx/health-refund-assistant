# Catálogo de arquivos JSON

Os JSONs da aplicação ficam centralizados em [`json/`](../../json/), organizados por
processo. Os arquivos obrigatórios das plataformas continuam em seus caminhos fixos:
`.devcontainer/devcontainer.json` e `src/extension/manifest.json`.

## Para onde os dados vão

1. A extensão do Chrome baixa a exportação para Downloads do usuário.
2. Ao importar pela interface Streamlit, a aplicação valida o período e grava uma cópia
   em `json/plan/imports/`, com prefixo de data/hora. O original em Downloads não é
   movido.
3. Um PDF enviado pelo navegador é usado durante a solicitação. O PDF não é salvo
   na memória, mas campos extraídos, perguntas, respostas e evidências da última
   análise podem ser persistidos na memória local.
4. No processamento em lote, os PDFs de `data/incoming/` são movidos para
   `data/processed/` ou `data/failed/`. Campos extraídos, hashes e referências ficam
   em `json/documents/state/notas_extraidas.json`.
5. Os relatórios de avaliação e conciliação ficam em pastas de processo separadas sob
   `json/`. São saídas locais regeneráveis, não datasets de entrada.

Exportações reais, estado e relatórios podem conter dados pessoais/de saúde e são
ignorados pelo Git. JSONs em `json/tests/synthetic/` são fictícios e versionáveis.
Os PDFs sintéticos ficam em `data/sinteticos/documentos/`.

## Inventário

| Caminho do JSON | Tipo e finalidade | Produzido por / consumido por | Schema e documentação |
|---|---|---|---|
| `json/config/mapeamento_reembolsos.json` | Configuração dos campos e critérios de conciliação | Revisado por pessoa; lido pelo conciliador e assistente | [Schema](../../json/reconciliation/schemas/mapping_config.schema.json) · [Guia](../../json/config/mapeamento_reembolsos.md) |
| `json/config/mapeamento_reembolsos.proposta.json` | Proposta local temporária, requer revisão | `mapping.py`; não substitui a configuração ativa | [Schema da proposta](../../json/reconciliation/schemas/mapping_proposal.schema.json) · [Guia](../../json/config/mapeamento_reembolsos.md) |
| `Downloads/careplus-reembolsos-*.json` | Exportação baixada pela extensão, antes da importação | Extensão Chrome; enviada pelo usuário à interface | [Schema](../../json/plan/schemas/plan_export.schema.json) · [Guia](../../src/extension/50_docs/10_exportacao_reembolsos.md) |
| `json/plan/imports/*.json` | Dataset importado do portal, com período e pedidos | Importação da interface; lido pela avaliação e conciliação | [Schema](../../json/plan/schemas/plan_export.schema.json) · [Guia do tipo](../../json/plan/imports/exportacao_plano.md) |
| `json/documents/state/notas_extraidas.json` | Estado operacional das extrações em lote | `pdf_processing.py`; lido por processamento e conciliação | [Schema](../../json/documents/schemas/notes_state.schema.json) · [Guia](../../json/documents/state/notas_extraidas.md) |
| `json/documents/state/conversa_local.json` | Conversa e última análise de um usuário local | Interface do assistente; saída local não criptografada | [Privacidade](../../README.md#memória-e-privacidade) |
| `json/evaluation/reports/*.json` | Métricas do VLM por execução/versão de prompt | `case_evaluation.py`; saída local | [Schema](../../json/evaluation/schemas/vlm_evaluation_report.schema.json) · [Guia](../../json/evaluation/reports/avaliacao.md) |
| `json/reconciliation/reports/*.json` | Candidatos e evidências da conciliação | `reconciliation.py`; saída local | [Schema](../../json/reconciliation/schemas/reconciliation_report.schema.json) · [Guia](../../json/reconciliation/reports/conciliacao.md) |
| `json/tests/synthetic/casos_teste.json` | Manifesto dos cenários, documentos e perguntas fictícias | Gerador; lido pelo benchmark | [Schema](../../json/tests/schemas/test_cases.schema.json) · [Guia](../../json/tests/synthetic/casos_teste.md) |
| `json/tests/synthetic/gabarito.json` | Ground truth isolado; nunca enviado ao prompt | Gerador; lido pelo avaliador | [Schema](../../json/tests/schemas/test_gold.schema.json) · [Guia](../../json/tests/synthetic/gabarito.md) |
| `json/tests/synthetic/exportacao_ficticia.json` | Dataset fictício para os testes determinísticos | Gerador; lido pelos testes | [Schema](../../json/plan/schemas/plan_export.schema.json) · [Guia](../../json/tests/synthetic/exportacao_ficticia.md) |
| `json/tests/templates/*.template.json` | Templates-fonte do manifesto e gabarito | Mantidos por desenvolvedores; copiados pelo gerador | [Guias](../../json/tests/templates/README.md) |
| `json/*/schemas/*.schema.json` | Contratos estruturais usados pelo código e prompts | Validadores locais e API OpenAI | [Índice de schemas](../../json/schemas/README.md); cada schema tem um `.md` adjacente |
| `.devcontainer/devcontainer.json` | Configuração externa do Codespaces/Dev Containers | GitHub Codespaces e VS Code | [Guia](../../.devcontainer/devcontainer.md) |
| `src/extension/manifest.json` | Metadados externos da extensão Chrome MV3 | Google Chrome | [Guia](../../src/extension/50_docs/11_manifest.md) |

Os arquivos importados e relatórios variam por execução; seus guias documentam o tipo,
sem criar um `.md` para cada cópia. Assim evitamos duplicação e não reproduzimos nomes
potencialmente pessoais.
