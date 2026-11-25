# 📚 Índice de Documentação

**Trabalho Final — Opção A | Entrega: 02/12/2026**

---

## 🚀 Comece Aqui (01_quickstart/)

Leia nesta ordem para começar rapidamente:

1. **[01_comece_aqui.md](./01_quickstart/01_comece_aqui.md)** ⭐⭐⭐
   - 3 passos para configurar Codespaces
   - Tempo: 1 minuto
   - **COMECE AQUI**

2. **[02_quick_reference.md](./01_quickstart/02_quick_reference.md)**
   - Referência rápida de comandos
   - Atalhos úteis

---

## ⚙️ Fluxo e Processo (02_process/)

Entenda como o sistema funciona:

1. **[01_rastreamento_testes.md](./02_process/01_rastreamento_testes.md)**
   - Sistema automático de rastreamento de testes
   - Como executar com `test_tracker.py`
   - Opções de execução (todos, específico, relatório)

---

## 📋 Requisitos e Escopo (03_requirements/)

Documentação de requisitos e respostas:

1. **[01_respostas_perguntas.md](./03_requirements/01_respostas_perguntas.md)** ⭐
   - Respostas às 3 perguntas específicas
   - GPT-6 Luna, Codespaces, rastreamento
   - Exemplos de uso

2. **[02_conferencia_final.md](./03_requirements/02_conferencia_final.md)**
   - Conferência final pré-entrega
   - Checklist de preparação

---

## ✅ Testes e Validação (04_testing/)

Teste e validação completa:

1. **[01_checklist_entrega.md](./04_testing/01_checklist_entrega.md)**
   - Checklist para preparação de entrega
   - Pré-requisitos validados

2. **[02_verificacao_completa.md](./04_testing/02_verificacao_completa.md)** ⭐⭐
   - Verificação completa de todas as 5 fases
   - Estatísticas de qualidade
   - Garantias finais

3. **[03_verificacao_codespaces_ui.md](./04_testing/03_verificacao_codespaces_ui.md)** ⭐⭐⭐
   - Teste completo com Codespaces + UI + 5 casos reais
   - Step-by-step para validação
   - 60 testes + UI + avaliação

---

## 🏛️ Arquitetura (05_architecture/)

Visão técnica e arquitetura:

1. **[01_visao_geral.md](./05_architecture/01_visao_geral.md)**
   - Visão geral de entrega
   - Guia de execução
   - Próximos passos

---

## 🔐 Segurança e Conformidade (06_security/)

Vazio (veja README.md raiz para informações de segurança)

---

## 📄 Documentação Técnica Formal

### Requisitos Técnicos (R1-R5)
- **[caderno_projeto.md](./caderno_projeto.md)**
  - R1: Problema e Valor
  - R2: Prompt Engineering (v1.0 → v4.0)
  - R3: Recurso de IA (VLM + JSON)
  - R4: Testes e Análise (60 testes + 5 casos)
  - R5: Segurança e Ética (LGPD, Prompt Injection)

### Resultados de Testes
- **[planilha_testes_5_casos.md](./planilha_testes_5_casos.md)**
  - Tabela com 5 casos de teste
  - Resultados REAIS (v4.0 com GPT-6 Luna)
  - Status: 5/5 ✅

---

## 🎯 Roteiros Rápidos

### Para Usar No Dia 02/12/2026

```
1. Descompactar ZIP
   $ unzip health-refund-assistant-entrega.zip

2. Ler documentação inicial
   $ cat docs/01_quickstart/01_comece_aqui.md

3. Criar Codespaces
   GitHub > Code > Codespaces > Create codespace on main

4. Executar testes com rastreamento
   $ python scripts/test_tracker.py --mode run --verbose

5. Revisar logs
   $ cat json/evaluation/reports/test_execution_*.json
```

### Para Executar Testes Localmente

```bash
# Todos os testes
pytest -v

# Com rastreamento automático
python scripts/test_tracker.py --mode run --verbose

# Teste específico
pytest tests/unit/test_extraction.py -v

# Teste com rastreamento específico
python scripts/test_tracker.py --mode test --name test_extraction
```

### Para Executar UI (Streamlit)

```bash
# Iniciar web app
streamlit run src/web_app.py

# Acesso: http://localhost:8501
```

---

## 📊 Estrutura de Arquivos

```
health-refund-assistant/
├── README.md                    # Visão técnica (único .md na raiz)
├── docs/
│   ├── INDEX.md                 # Este arquivo
│   ├── 01_quickstart/           # 🚀 Comece aqui
│   │   ├── 01_comece_aqui.md
│   │   └── 02_quick_reference.md
│   ├── 02_process/              # ⚙️ Fluxo
│   │   └── 01_rastreamento_testes.md
│   ├── 03_requirements/         # 📋 Requisitos
│   │   ├── 01_respostas_perguntas.md
│   │   └── 02_conferencia_final.md
│   ├── 04_testing/              # ✅ Testes
│   │   ├── 01_checklist_entrega.md
│   │   └── 02_verificacao_completa.md
│   ├── 05_architecture/         # 🏛️ Arquitetura
│   │   └── 01_visao_geral.md
│   ├── 06_security/             # 🔐 Segurança
│   ├── caderno_projeto.md       # Requisitos formais
│   └── planilha_testes_5_casos.md
├── src/                         # 💻 Código-fonte
│   ├── assistant.py             # Assistente principal
│   ├── vlm_extractor.py         # Extração VLM
│   ├── reconciliation.py        # Reconciliação
│   ├── assessment.py            # Auditoria
│   └── web_app.py               # UI Streamlit
├── scripts/                     # 🔧 Utilitários
│   ├── test_tracker.py          # Rastreamento de testes
│   ├── gerar_fixtures_sinteticas.py
│   └── case_evaluation_v3.py
├── tests/                       # ✅ 60 testes
│   ├── unit/
│   └── integration/
├── json/                        # 📊 Dados
│   ├── evaluation/reports/
│   ├── schemas/
│   ├── datasets/
│   └── documents/
├── data/                        # 📁 Dados de entrada
│   └── sinteticos/
└── .devcontainer/               # 🐳 Codespaces
    └── devcontainer.json
```

---

## 🎓 Leitura Recomendada Por Perfil

### Novo no Projeto (1 hora)
1. README.md (5 min)
2. docs/01_quickstart/01_comece_aqui.md (10 min)
3. docs/03_requirements/01_respostas_perguntas.md (20 min)
4. docs/04_testing/02_verificacao_completa.md (25 min)

### Revisor Técnico (2 horas)
1. docs/caderno_projeto.md (40 min) — R1-R5
2. docs/planilha_testes_5_casos.md (20 min) — Resultados
3. docs/02_process/01_rastreamento_testes.md (30 min)
4. docs/04_testing/02_verificacao_completa.md (30 min)

### Executor (Codespaces)
1. docs/01_quickstart/01_comece_aqui.md (3 passos)
2. python scripts/test_tracker.py --mode run --verbose
3. Ver logs em json/evaluation/reports/

---

## ✅ Checklist Rápido

- [ ] Leu docs/01_quickstart/01_comece_aqui.md
- [ ] Criou Codespaces (GitHub > Code > Codespaces)
- [ ] Executou: `python scripts/test_tracker.py --mode run --verbose`
- [ ] Revisou logs em json/evaluation/reports/
- [ ] Leu docs/caderno_projeto.md (R1-R5)
- [ ] Leu docs/planilha_testes_5_casos.md (Resultados)
- [ ] Preparado para 02/12/2026

---

## 📞 Dúvidas Frequentes

**P: Por onde começar?**  
R: Leia `docs/01_quickstart/01_comece_aqui.md` (1 minuto)

**P: Como executar testes?**  
R: `python scripts/test_tracker.py --mode run --verbose`

**P: Como acessar a UI?**  
R: `streamlit run src/web_app.py` → http://localhost:8501

**P: Onde estão os logs?**  
R: `json/evaluation/reports/test_execution_*.json`

**P: Pronto para entregar?**  
R: Veja `docs/04_testing/02_verificacao_completa.md`

---

## 🔗 Links Úteis

- [README.md](../README.md) — Visão técnica
- [caderno_projeto.md](./caderno_projeto.md) — Requisitos formais
- [planilha_testes_5_casos.md](./planilha_testes_5_casos.md) — Resultados
- Código-fonte: [src/](../src/)
- Testes: [tests/](../tests/)
- Scripts: [scripts/](../scripts/)

---

**Última atualização:** 25 de novembro de 2026  
**Status:** 🟢 DOCUMENTAÇÃO COMPLETA  
**Pronto para:** 02/12/2026
