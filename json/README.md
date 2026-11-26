# JSONs da aplicação

Todos os JSONs mantidos pela aplicação ficam centralizados aqui, separados por
processo. Os caminhos são definidos em
[`src/health_refund_assistant/core/paths.py`](../src/health_refund_assistant/core/paths.py).

## Estrutura

```text
json/
├── extraction/
│   └── schemas/                     # Contratos VLM por versão, inclusive v4.2
├── reconciliation/
│   ├── schemas/                     # Contratos: mapping_config, mapping_proposal, reconciliation_report
│   └── reports/                     # Relatórios de conciliação
├── plan/
│   ├── schemas/                     # Contrato: plan_export.schema.json
│   └── imports/                     # Exportações do plano importadas
├── documents/
│   ├── schemas/                     # Contrato: notes_state.schema.json
│   └── state/                       # Extrações e índice dos PDFs processados
├── evaluation/
│   ├── schemas/                     # Contrato: vlm_evaluation_report.schema.json
│   └── reports/                     # Relatórios do benchmark VLM
├── tests/
│   ├── schemas/                     # Contratos: test_cases.schema.json, test_gold.schema.json
│   ├── templates/                   # Templates-fonte de casos e gabaritos
│   └── synthetic/                   # JSONs fictícios usados na bateria
├── config/                          # Configuração ativa e propostas revisáveis
└── schemas/                         # [LEGADO] Vazio; schemas migraram para suas pastas
```

## Como funciona

1. **Schemas** agora são colocados com seus processos:
   - `extraction/schemas/` → VLM extraction
   - `reconciliation/schemas/` → Conciliação e mapeamento
   - `plan/schemas/` → Importação do plano
   - `documents/schemas/` → Processamento de documentos
   - `evaluation/schemas/` → Avaliação de modelos
   - `tests/schemas/` → Dados de teste

2. **Código carrega dinamicamente** via `core/paths.py`:
   ```python
   from health_refund_assistant.core.paths import resolve_schema
   from health_refund_assistant.core.json_contracts import carregar_schema_json
   
   schema = carregar_schema_json("vlm_extraction.schema.json")
   # Mapeia automaticamente para json/extraction/schemas/vlm_extraction.schema.json
   ```

3. **Cada pasta de schemas tem um README** explicando:
   - Qual schema faz o quê
   - Quais arquivos o usam
   - Como o código acessa

4. **Documentação** fica junto:
   - Cada `*.schema.json` tem um `*.schema.md` ao lado
   - READMEs explicam o fluxo de dados
   - Links para código e prompts

## Dados locais

Exportações, estado e relatórios são ignorados pelo Git:
- `json/plan/imports/*.json` → dados do plano (pessoais/saúde)
- `json/documents/state/*.json` → histórico de processamento
- `json/reconciliation/reports/*.json` → relatórios gerados
- `json/evaluation/reports/*.json` → resultados de benchmark

Schemas, configuração e fixtures sintéticas também são versionados; dados reais
e saídas locais não devem ser incluídos.

## Exceções obrigatórias

- `.devcontainer/devcontainer.json` → Codespaces/Dev Containers
- `extension/manifest.json` → Chrome Web Store
- Downloads → Extensão baixa exportações; cópia em `json/plan/imports/`

Veja o [catálogo JSON](../docs/70_documentation/05_json_catalogo.md) para o fluxo de dados.
