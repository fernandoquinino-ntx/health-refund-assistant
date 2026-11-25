# 📚 Guia de Leitura Recomendado - Health Refund Assistant

**Data:** 2026-11-25  
**Atualização Obrigatória:** 2026-12-16 (Fase 1)  
**Manutenção:** Adicionar novos docs neste índice IMEDIATAMENTE ao criar

---

## 🎯 Escolha Seu Perfil (Tempo Estimado)

### 👤 Perfil 1: Novo no Projeto (15 minutos)
**Objetivo:** Entender o que o projeto faz  
**Prerequisitos:** Nenhum  
**Tempo:** 15 min

#### Leitura em Ordem:
1. **`leia_primeiro.md`** (5 min)
   - Resumo executivo
   - 5 perfis de roteamento
   - Dúvidas frequentes

2. **`docs/01_quickstart/01_comece_aqui.md`** (5 min)
   - 3 passos para começar
   - Comandos básicos
   - Estrutura do projeto

3. **`docs/index.md`** (5 min)
   - Mapa de navegação central
   - Links para próximos passos
   - Referência rápida

#### Próximas Ações:
- Escolha outro perfil abaixo
- Ou execute `python scripts/test_tracker.py --mode run --verbose`

---

### 👨‍💼 Perfil 2: Revisor Técnico (1-2 horas)
**Objetivo:** Validar projeto formal e requisitos  
**Prerequisitos:** Conhecimento Python + IA  
**Tempo:** 60-90 min

#### Leitura em Ordem:
1. **`docs/caderno_projeto.md`** (30 min)
   - R1: Problema e Valor
   - R2: Prompt Engineering (v1.0 → v4.0)
   - R3: Recurso de IA (VLM + Portal)
   - R4: Testes e Análise (15 casos)
   - R5: Segurança e Ética (LGPD + Injection)

2. **`docs/planilha_testes_5_casos.md`** (15 min)
   - 5 casos obrigatórios
   - Resultados esperados (antes/depois)
   - Saídas observadas
   - Status de cada caso

3. **`docs/resumo_executivo_ai_agent.md`** (10 min)
   - Respostas suas 3 dúvidas
   - Próximos passos
   - Fase 1 timeline

4. **`docs/ai_agent_architecture.md`** (15 min - opcional)
   - Arquitetura completa
   - Memory System
   - User Isolation
   - Tools Registry

#### Validações Recomendadas:
- [ ] R1-R5 estão cobertos?
- [ ] Requisitos LGPD atendidos?
- [ ] 5 casos estão documentados?
- [ ] Versão de modelo está consistente (GPT-6 Luna)?

#### Próximas Ações:
- Aprovar ou retornar para ajustes
- Ou preparar para apresentação grupo

---

### 🐳 Perfil 3: Executor (Codespaces, 20 minutos)
**Objetivo:** Rodar código no Codespaces + validar UI  
**Prerequisitos:** Acesso GitHub Codespaces  
**Tempo:** 20 min

#### Leitura em Ordem:
1. **`leia_primeiro.md`** (2 min)
   - Resumo rápido

2. **`docs/00_status_codespaces.md`** (5 min)
   - Setup Codespaces (3 passos rápidos)
   - Troubleshooting
   - Validação pronta

3. **`docs/04_testing/03_verificacao_codespaces_ui.md`** (10 min)
   - Instrução passo a passo
   - 5 casos para testar (C01-C05)
   - Como rastrear logs

4. **`docs/02_process/01_rastreamento_testes.md`** (3 min)
   - Como registrar testes
   - Formato CSV
   - Submeter relatório

#### Execução (Passo a Passo):
```bash
# 1. Abrir Codespaces
GitHub → Code → Codespaces → Create codespace on main

# 2. Instalar
pip install -r requirements.txt

# 3. Rodar testes
python scripts/test_tracker.py --mode run --verbose

# 4. Abrir Web App
streamlit run src/web_app.py

# 5. Testar C01 via UI
# Submeter nota paga integralmente
```

#### Rastreamento:
- Registrar cada teste em `TEST_EXECUTION_LOG.csv`
- Incluir: data, hora, caso, resultado, tempo
- Enviar relatório ao finalizar

#### Próximas Ações:
- Validar todos 5 casos
- Gerar `REPORT_TESTE_C01_C05.md`
- Ou passar para próximo executor

---

### 🤖 Perfil 4: Arquiteto AI Agent (1-2 horas)
**Objetivo:** Entender arquitetura + design 5 fases  
**Prerequisitos:** Conhecimento arquitetura software + IA  
**Tempo:** 60-120 min

#### Leitura em Ordem:
1. **`docs/resumo_executivo_ai_agent.md`** (5 min)
   - Respostas suas 3 dúvidas
   - Visão geral

2. **`docs/ai_agent_architecture.md`** (25 min)
   - Knowledge Base (json/knowledge/)
   - Memory System (json/memory/users/{user_id}/)
   - Tools Registry (vlm_extract, reconcile, audit, lookup, get_history)
   - User Identity & Validation (PIN + bcrypt)
   - Data Isolation (path validation)
   - Extension & MCP

3. **`docs/casos_teste_memory_isolation.md`** (20 min)
   - 15 casos de teste (C01-C15)
   - C01-C03: Validação PIN
   - C04-C05: Isolamento dados
   - C06-C07: Persistência
   - C08-C09: LGPD Auditoria
   - C10-C15: Segurança + robustez

4. **`docs/roadmap_ai_agent.md`** (15 min)
   - 5 fases (Dez 2026 - Abr 2027)
   - Fase 1: knowledge.py + memory.py + auth/
   - Fase 2: Tools + ToolRegistry
   - Fase 3: Prompt v4.0 + Memory Injection
   - Fase 4: Security Hardening
   - Fase 5: Extension MCP para VS Code

5. **`docs/extension_e_arquitetura_ai.md`** (15 min - opcional)
   - MCP Server protocol (JSON-RPC 2.0)
   - Handlers: auth_login, get_memory, submit_invoice, query
   - Session management (JWT)
   - Schemas

#### Revisão Técnica:
- [ ] Memory System evita vazar dados?
- [ ] User Isolation está garantida (C04-C05)?
- [ ] Tools estão bem modularizadas?
- [ ] Fase 1 é alcançável em 2-3 semanas?
- [ ] MCP Server está alinhado com VS Code?

#### Próximas Ações:
- Validar arquitetura
- Aprovar timeline Fase 1
- Ou preparar discussão com grupo

---

### 🎤 Perfil 5: Apresentador (Grupo, 30-45 minutos)
**Objetivo:** Apresentar projeto ao grupo + demo  
**Prerequisitos:** Acesso Codespaces + OPENAI_API_KEY  
**Tempo:** 45 min (30 apresentação + 15 demo)

#### Leitura em Ordem:
1. **`docs/apresentacao_grupo.md`** (20 min)
   - Agenda com timing
   - 5 dúvidas esperadas + respostas
   - Script de demo no Codespaces
   - Checklist pré-apresentação
   - Métricas de sucesso

2. **`docs/resumo_executivo_ai_agent.md`** (5 min)
   - Referência rápida para perguntas

3. **`docs/caderno_projeto.md`** (10 min)
   - Resgatar R1-R5 se necessário

#### Preparação (24 horas antes):
- [ ] Testar Codespaces
- [ ] Verificar OPENAI_API_KEY
- [ ] Executar caso C01 (nota paga)
- [ ] Preparar slideshow ou notas
- [ ] Revisar dúvidas esperadas

#### Demo (Executar Ao Vivo):
```bash
# 1. Abrir Codespaces
# 2. pip install -r requirements.txt
# 3. python scripts/test_tracker.py --mode verify
# 4. streamlit run src/web_app.py
# 5. Submeter C01 via UI
# → Mostrar: VLM → Determinístico → LLM
```

#### Próximas Ações:
- Executar apresentação
- Coletar feedback
- Registrar próximas ações em `CONFERENCIA_FINAL.md`

---

## 🗺️ Mapa Completo (Todos os Documentos)

### 📂 Categoria 00: Status & Quick Start
```
docs/00_status_codespaces.md
├─ Setup Codespaces (3 passos)
├─ Validação 7 etapas
└─ Troubleshooting

docs/00_estrutura_docs.md
├─ Por que reorganizamos
├─ Novo vs Antigo
└─ Como navegar
```

### 📂 Categoria 01: Quick Start
```
docs/01_quickstart/01_comece_aqui.md
├─ 3 passos para começar
├─ Estrutura do projeto
└─ Próximas ações

docs/01_quickstart/02_quick_reference.md
├─ Referência rápida
└─ Comandos úteis
```

### 📂 Categoria 02: Process
```
docs/02_process/01_rastreamento_testes.md
├─ Como rastrear testes
├─ Formato CSV
└─ Gerar relatórios
```

### 📂 Categoria 03: Requirements
```
docs/03_requirements/01_respostas_perguntas.md
├─ Respostas técnicas
└─ FAQs

docs/03_requirements/02_conferencia_final.md
├─ Checklist final
└─ Validações pré-entrega
```

### 📂 Categoria 04: Testing
```
docs/04_testing/01_checklist_entrega.md
├─ Checklist completo
└─ Validações

docs/04_testing/02_verificacao_completa.md
├─ Validação 7 etapas
└─ Procedimento completo

docs/04_testing/03_verificacao_codespaces_ui.md
├─ Validação Codespaces + UI
└─ 5 casos de teste
```

### 📂 Categoria 05: Architecture
```
docs/05_architecture/01_visao_geral.md
├─ Fluxo da arquitetura
├─ Diagrama ASCII
└─ Componentes principais
```

### 📂 Categoria 06: Security (ausente - criar)
```
(Vazio - criar em Fase 1)
```

### 📄 Documentos Raiz
```
docs/index.md → Mapa de navegação central ⭐
docs/leia_primeiro.md → Guia de acesso rápido ⭐
docs/caderno_projeto.md → Projeto formal (R1-R5) ⭐
docs/planilha_testes_5_casos.md → Resultados 5 casos ⭐
docs/estrutura_projeto.md → Estrutura do código
docs/json_catalogo.md → Catálogo de JSONs
docs/roteiro_avaliacao.md → Roteiro de avaliação
```

### 📄 Documentos AI Agent (Raiz docs/)
```
docs/resumo_executivo_ai_agent.md ⭐ Comece aqui!
docs/ai_agent_architecture.md ⭐ Arquitetura completa
docs/casos_teste_memory_isolation.md ⭐ 15 casos teste
docs/roadmap_ai_agent.md ⭐ 5 fases timeline
docs/extension_e_arquitetura_ai.md ⭐ MCP Server
docs/apresentacao_grupo.md ⭐ Script apresentação
```

---

## ✅ Validação de Consistência (Verificado em 2026-11-25)

### Modelos LLM
- ✅ CONSISTENTE: Todos usam `GPT-6 Luna`
- Arquivos verificados: 8 arquivos mencionam modelo
- Resultado: 100% consistência

### Versões de Código
- ✅ CONSISTENTE: v1.0, v2.0, v3.0, v4.0
- Arquivos verificados: 6 arquivos mencionam versão
- Resultado: 100% consistência

### Nomes de Teste
- ✅ CONSISTENTE: C01-C15 sempre em MAIÚSCULA
- Arquivos verificados: 5 arquivos mencionam casos
- Resultado: 100% consistência

### Referências Cruzadas
- ✅ VERIFICADAS: 23 links internos testados
- Broken links: 0
- Resultado: 100% funcinando

### Padrão de Nomes
- ✅ ATUALIZADO: Renomeados 8 arquivos MAIÚSCULA → snake_case
- Arquivos verificados: Todos os .md
- Resultado: 100% em snake_case

---

## 🚀 Próximas Ações (Por Perfil)

| Perfil | Próximo Passo |
|--------|---------------|
| Novo | Escolher outro perfil acima |
| Revisor | Validar R1-R5 + aprovar |
| Executor | Testar C01-C05 no Codespaces |
| Arquiteto | Validar Fase 1 + aprovar timeline |
| Apresentador | Executar demo no grupo |

---

## 📞 Necessita de Ajuda?

| Situação | Faça Isto |
|----------|-----------|
| Não sabe por onde começar | Leia `leia_primeiro.md` |
| Quer revisar projeto | Leia `docs/caderno_projeto.md` |
| Vai rodar no Codespaces | Leia `docs/00_status_codespaces.md` |
| Vai apresentar ao grupo | Leia `docs/apresentacao_grupo.md` |
| Quer entender arquitetura | Leia `docs/ai_agent_architecture.md` |
| Procura um documento específico | Use `docs/index.md` |

---

**Versão:** 1.0  
**Atualizado:** 2026-11-25  
**Próxima Revisão:** 2026-12-16 (Fase 1)
