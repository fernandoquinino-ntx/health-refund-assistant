# Estrutura do projeto

O código executável fica em um pacote Python instalado em modo editável. Cada módulo
tem uma responsabilidade principal; a interface não contém as regras do bot nem
implementa diretamente chamadas aos modelos.

```text
health-refund-assistant/
├── app.py
├── pyproject.toml
├── requirements.txt
├── src/
│   └── health_refund_assistant/
│       ├── assistant.py
│       ├── web_app.py
│       ├── pdf_processing.py
│       ├── pdf_converter.py
│       ├── vlm_extractor.py
│       ├── plan_exports.py
│       ├── assessment.py
│       ├── reconciliation.py
│       ├── case_evaluation.py
│       ├── mapping.py
│       └── paths.py
├── prompts/
├── json/
│   ├── config/
│   ├── documents/state/
│   ├── evaluation/reports/
│   ├── plan/imports/
│   ├── reconciliation/reports/
│   ├── schemas/
│   └── tests/
│       ├── templates/
│       └── synthetic/
├── data/
├── extension/
├── scripts/
├── tests/
├── docs/
└── .devcontainer/
```

## Responsabilidades dos módulos Python

| Módulo | Responsabilidade |
|---|---|
| [app.py](../app.py) | Inicializar a interface Streamlit; sem regras de negócio. |
| [assistant.py](../src/health_refund_assistant/assistant.py) | Receber `AssistantRequest`, validar entradas, coordenar extração, análise determinística e resposta; é o ponto de entrada do bot. |
| [web_app.py](../src/health_refund_assistant/web_app.py) | Renderizar a interface, importar arquivos e converter ações do usuário em uma chamada a `handle_request`. |
| [pdf_processing.py](../src/health_refund_assistant/pdf_processing.py) | Processar PDFs em lote, evitar duplicatas e organizar arquivos processados/falhos. |
| [pdf_converter.py](../src/health_refund_assistant/pdf_converter.py) | Converter uma página do PDF para imagem. |
| [vlm_extractor.py](../src/health_refund_assistant/vlm_extractor.py) | Cliente OpenAI multimodal, versões do prompt de extração, JSON Schema e validação da saída. |
| [plan_exports.py](../src/health_refund_assistant/plan_exports.py) | Importar e validar exportações JSON, inclusive o período consultado. |
| [assessment.py](../src/health_refund_assistant/assessment.py) | Regras de completude, janela simulada de 30 dias e cobertura temporal. |
| [reconciliation.py](../src/health_refund_assistant/reconciliation.py) | Normalizar registros do plano e gerar candidatas explicáveis de conciliação. |
| [case_evaluation.py](../src/health_refund_assistant/case_evaluation.py) | Executar benchmark do VLM; manter o gabarito fora das chamadas ao modelo. |
| [mapping.py](../src/health_refund_assistant/mapping.py) | Ferramenta opcional para propor e validar mapeamentos de schema. |
| [paths.py](../src/health_refund_assistant/paths.py) | Centralizar caminhos para dados, prompts e configuração do repositório. |

O bot é atualmente chamado pela interface Streamlit, não por uma API HTTP separada.
Uma futura interface FastAPI pode ser adicionada como adaptador e chamar
`assistant.handle_request` sem duplicar regras ou chamadas de modelo.

## Dados e prompts

| Diretório | Uso |
|---|---|
| `data/incoming/` | PDFs locais disponíveis para seleção na interface e processamento em lote. |
| `data/processed/`, `data/failed/` | Arquivo local dos resultados do processamento em lote. |
| `data/sinteticos/documentos/` | PDFs fictícios da bateria; os JSONs de teste estão centralizados em `json/tests/synthetic/`. |
| `json/plan/imports/` | Cópias locais das exportações JSON importadas do portal. |
| `json/documents/state/` | Estado local das extrações e dos PDFs processados. |
| `json/evaluation/reports/` | Relatórios JSON regeneráveis do benchmark VLM. |
| `json/reconciliation/reports/` | Relatórios JSON regeneráveis da conciliação. |
| `json/tests/synthetic/` | Manifesto, ground truth e exportação fictícia executáveis. |
| `json/tests/templates/` | Templates-fonte do manifesto e do gabarito. |
| `json/extraction/schemas/` | Contratos para extração visual (vlm_extraction, v4). |
| `json/reconciliation/schemas/` | Contratos para conciliação (mapping_config, mapping_proposal, reconciliation_report). |
| `json/plan/schemas/` | Contrato para importação de plano (plan_export). |
| `json/documents/schemas/` | Contrato para estado de documentos (notes_state). |
| `json/evaluation/schemas/` | Contrato para avaliação (vlm_evaluation_report). |
| `json/tests/schemas/` | Contratos para dados de teste (test_cases, test_gold). |
| `json/schemas/` | [LEGADO] Vazio; schemas migraram para suas pastas temáticas. |
| `json/config/` | Configuração versionada do mapeamento e propostas locais temporárias. |
| `prompts/vlm_extractor/` | Prompts de extração visual, versionados separadamente. |
| `prompts/reembolso_assistente/` | Prompts que formulam respostas com base nas evidências calculadas. |
| `prompts/reembolso_status/` | Prompt usado pela ferramenta opcional de mapeamento. |

O gerador em `scripts/` lê templates de `json/tests/templates/`, grava JSONs em
`json/tests/synthetic/` e cria PDFs em `data/sinteticos/documentos/`. Nunca coloque
dados reais em fixtures compartilhadas.

O [catálogo JSON](./json_catalogo.md) mostra cada caminho, sua finalidade, produtor,
consumidor, schema e documentação Markdown específica.

## Catálogo e contratos JSON

Consulte o [catálogo JSON](./json_catalogo.md) e o índice em [`json/README.md`](../json/README.md).
Cada schema tem documentação Markdown adjacente. Quando um schema é contrato de um
prompt, a documentação do schema referencia o prompt, e o próprio prompt aponta para
o caminho do schema.

## Diretórios mantidos e limpeza

Os diretórios `extension/`, `scripts/`, `json/`, `prompts/` e
`data/sinteticos/documentos/` têm consumidores ativos; não são sobras. PDFs pessoais
em `data/` e JSONs locais nas pastas de importação, estado e relatórios de `json/` são
ignorados pelo Git. Os metadados `.devcontainer/devcontainer.json` e
`extension/manifest.json` permanecem em caminhos fixos exigidos pelas plataformas.

`__pycache__/`, `.venv/`, `.env` e `.DS_Store` são artefatos locais, não componentes
do projeto. O `.gitignore` os exclui. `.venv/` e `.env` não devem ser apagados como
parte da reorganização: podem conter o ambiente e as configurações locais do usuário.

## Convenções de desenvolvimento

- Instale o pacote em modo editável com `python -m pip install -r requirements.txt`;
  as dependências e o nome do pacote ficam declarados em `pyproject.toml`.
- Execute os módulos como `python -m health_refund_assistant.<módulo>`, não por
  caminhos relativos a `src/`.
- Mantenha gabaritos de avaliação fora do prompt e use dados sintéticos em CI e
  Codespaces.
- Mudanças de prompt devem criar nova versão e rodar a mesma bateria, sem sobrescrever
  o histórico.
- Segredos ficam em variáveis de ambiente/Codespaces Secrets; documentos reais não
  devem ser enviados ao Git nem a ambientes compartilhados.
