# 📍 Mapa da Estrutura de Documentação

**Última atualização:** 2026-11-25  
**Padrão:** Números ordinais (NN_) + snake_case  
**Modelo LLM atual:** GPT-6 Luna

---

## 🎯 Ordem de Leitura Recomendada

### Para NOVO USUÁRIO (15 min)
1. **[01_leia_primeiro.md](/01_leia_primeiro.md)** — Bem-vindo ao projeto
2. **[docs/10_quickstart/01_comece_aqui.md](/docs/10_quickstart/01_comece_aqui.md)** — Setup rápido
3. **[docs/70_documentation/01_index.md](/docs/70_documentation/01_index.md)** — Visão geral

### Para REVISOR (1-2h)
1. **[01_leia_primeiro.md](/01_leia_primeiro.md)**
2. **[02_copilot_guidelines.md](/02_copilot_guidelines.md)** — Diretrizes permanentes
3. **[docs/60_project/01_caderno_projeto.md](/docs/60_project/01_caderno_projeto.md)** — Projeto formal
4. **[docs/50_architecture/01_visao_geral.md](/docs/50_architecture/01_visao_geral.md)** — Arquitetura

### Para EXECUTOR CODESPACES (20 min)
1. **[docs/40_testing/03_verificacao_codespaces_ui.md](/docs/40_testing/03_verificacao_codespaces_ui.md)** — Como rodar UI
2. **[docs/70_documentation/10_status_codespaces.md](/docs/70_documentation/10_status_codespaces.md)** — Status atual
3. **[docs/40_testing/01_checklist_entrega.md](/docs/40_testing/01_checklist_entrega.md)** — Checklist

### Para ARQUITETO AI AGENT (1-2h)
1. **[02_copilot_guidelines.md](/02_copilot_guidelines.md)**
2. **[docs/50_architecture/02_ai_agent_architecture.md](/docs/50_architecture/02_ai_agent_architecture.md)** — Arquitetura AI
3. **[docs/50_architecture/03_extension_arquitetura.md](/docs/50_architecture/03_extension_arquitetura.md)** — Extension
4. **[docs/70_documentation/06_casos_teste_memory.md](/docs/70_documentation/06_casos_teste_memory.md)** — Memory Isolation

### Para APRESENTADOR GRUPO (30-45 min)
1. **[docs/60_project/02_apresentacao_grupo.md](/docs/60_project/02_apresentacao_grupo.md)** — Script apresentação
2. **[docs/60_project/01_caderno_projeto.md](/docs/60_project/01_caderno_projeto.md)** — Projeto R1-R5
3. **[docs/40_testing/01_checklist_entrega.md](/docs/40_testing/01_checklist_entrega.md)** — Checklist final

---

## 📚 Estrutura Completa

```
health-refund-assistant/
├── README.md                          # Bem-vindo (GitHub)
├── 01_leia_primeiro.md               # Entrada principal
├── 02_copilot_guidelines.md          # Diretrizes permanentes
│
└── docs/
    ├── 10_quickstart/
    │   ├── 01_comece_aqui.md         # Setup inicial
    │   └── 02_quick_reference.md     # Referência rápida
    │
    ├── 20_process/
    │   └── 01_rastreamento_testes.md # Como rastrear testes
    │
    ├── 30_requirements/
    │   ├── 01_respostas_perguntas.md # R1-R5 do projeto
    │   └── 02_conferencia_final.md   # Check-in final
    │
    ├── 40_testing/
    │   ├── 01_checklist_entrega.md   # Checklist
    │   ├── 02_verificacao_completa.md # Verificações
    │   └── 03_verificacao_codespaces_ui.md # Codespaces
    │
    ├── 50_architecture/
    │   ├── 01_visao_geral.md         # VLM + Reconciliador + LLM
    │   ├── 02_ai_agent_architecture.md # AI Agent design
    │   └── 03_extension_arquitetura.md # VS Code Extension
    │
    ├── 60_project/
    │   ├── 01_caderno_projeto.md     # Projeto formal (R1-R5)
    │   ├── 02_apresentacao_grupo.md  # Apresentação 09/12
    │   └── 03_roadmap_ai_agent.md    # Roadmap Fase 1-3
    │
    └── 70_documentation/
        ├── 01_index.md               # Hub central
        ├── 02_guia_leitura_recomendado.md # Ordem por perfil
        ├── 03_audit_consistencia.md  # Auditoria (atualizado)
        ├── 04_estrutura_projeto.md   # Pastas e arquivos
        ├── 05_json_catalogo.md       # Catálogo de JSONs
        ├── 06_casos_teste_memory.md  # Memory isolation
        ├── 07_planilha_testes_5_casos.md # Testes formais
        ├── 08_roteiro_avaliacao.md   # Avaliação de versões
        ├── 09_resumo_executivo.md    # Resumo AI Agent
        ├── 10_status_codespaces.md   # Status atual
        └── 11_estrutura_docs.md      # (anterior)
```

---

## 🔑 Padrões de Nomenclatura

### Markdown Files
- **Raiz:** `NN_nome_arquivo.md` (01_leia_primeiro.md, 02_copilot_guidelines.md)
- **Subpastas:** `docs/NN_categoria/MM_nome_arquivo.md`
  - `10_quickstart/01_...`, `20_process/01_...`, etc.
  - Sempre `NN_` para ordenação visual clara

### Nomenclatura Regras
- ✅ **snake_case** (nomes_compostos_minusculos)
- ✅ **Sem espaços** nos nomes
- ✅ **Números ordinais** para ordenação (10_, 20_, 30_, etc.)
- ❌ **Nunca MAIÚSCULA** nos nomes
- ❌ **Nunca camelCase** ou `PascalCase`

### Modelos LLM
- ✅ **Grafia correta:** `GPT-6 Luna`
- ❌ **Nunca:** `gpt-6-luna`, `GPT-6-LUNA`, `gpt-6-Luna`

---

## 🧪 Funcionalidades Implementadas

| Funcionalidade | Arquivo | Status | Versão |
|---|---|---|---|
| VLM Extractor | `src/vlm_extractor.py` | ✅ | v4.0 |
| Reconciliador | `src/reconciliation.py` | ✅ | - |
| Assessor | `src/assessment.py` | ✅ | - |
| Assistente | `src/assistant.py` | ✅ | - |
| Web App | `app.py` | ✅ | - |
| Fixtures Sintéticas | `scripts/gerar_fixtures_sinteticas.py` | ✅ | - |
| Avaliação de Casos | `scripts/case_evaluation_v3.py` | ✅ | v3 |
| Rastreamento Testes | `scripts/test_tracker.py` | ✅ | - |
| JSON Schemas | `json/*/schemas/` | ✅ | - |
| Prompts (v1-v4) | `prompts/vlm_extractor/` | ✅ | v4.0 |
| Unit Tests | `tests/test_*.py` | ✅ | 11 arquivos |

---

## 🗂️ Pastas Principais

```
src/health_refund_assistant/
├── __init__.py
├── assistant.py        # Assistente LLM principal
├── assessment.py       # Auditoria pré-envio
├── conciliation.py    # Reconciliação
├── reconciliation.py  # (renamed conciliation)
├── utils.py
├── paths.py           # Referência centralizada de caminhos
└── vlm_extractor.py   # Extração VLM (GPT-6 Luna)

json/
├── extraction/
│   ├── schemas/
│   └── reports/
├── reconciliation/
│   ├── schemas/
│   └── reports/
├── assessment/
│   ├── schemas/
│   └── reports/
├── config/
├── documents/
├── plan/
│   ├── imports/
│   └── schemas/
└── tests/
    └── synthetic/

prompts/
├── vlm_extractor/
│   ├── v1.0.txt
│   ├── v2.0.txt
│   ├── v3.0.txt
│   └── v4.0.txt
├── reembolso_assistente/
│   └── v1.0.txt
├── reembolso_status/
│   └── v1.0.txt
└── prompt_library.md

data/
├── processed/
└── sinteticos/

tests/
├── test_assessment.py
├── test_assistant.py
├── test_avaliar_casos.py
├── test_conciliar_reembolsos.py
├── test_json_schemas.py
├── test_plan_exports.py
├── test_processar_pdfs.py
├── test_synthetic_scenarios.py
├── test_vlm_extractor.py
└── test_web_app.py
```

---

## 🔄 Rastreamento de Versões

### Modelos LLM
- **Atual:** `GPT-6 Luna`
- **Anterior:** `gpt-4o-mini` (descontinuado)
- **Data de migração:** 2026-11-25

### Versionamento de Prompts
- VLM Extractor: v1.0 → v2.0 → v3.0 → v4.0 ✅
- Reembolso Assistente: v1.0 ✅
- Reembolso Status: v1.0 ✅

### Versionamento de Código
- VLM Extractor: v4.0
- Case Evaluation: v3
- Test Tracker: v1

---

## ✅ Checklist de Consistência

Verificado em 2026-11-25:

- [x] Todos os arquivos `.md` em **snake_case**
- [x] Todos os arquivos com **números ordinais** (NN_)
- [x] Nenhum arquivo em MAIÚSCULA
- [x] Todos os modelos LLM como **"GPT-6 Luna"**
- [x] Lixo removido (cache, .pyc, .DS_Store)
- [x] Funcionalidades core implementadas
- [x] 11 test files presentes
- [x] 4 versões de prompts (v1.0-v4.0)
- [x] Padrão de branch documentado
- [x] Rastreamento de testes configurado

---

## 📞 Próximos Passos

1. **Executar testes:** `pytest -v` (incluído em Codespaces)
2. **Rodar UI:** `python app.py` (Codespaces)
3. **Gerar fixtures:** `python scripts/gerar_fixtures_sinteticas.py`
4. **Avaliar casos:** `python scripts/case_evaluation_v3.py`
5. **Preparar entrega:** Seguir `docs/40_testing/01_checklist_entrega.md`

---

**Documento central de navegação** — sempre verifique aqui a ordem correta de leitura!
