# 🚀 Guia Rápido de Início - v2.0

**Projeto:** health-refund-assistant  
**Versão:** 2.0 (Reorganização completa + GPT-6 Luna)  
**Status:** ✅ Pronto para usar  
**Data:** 2026-11-25

---

## ⚡ 3 Passos para Começar

### Passo 1: Descompacte e Entre no Diretório
```bash
unzip health-refund-assistant-v2.0-final.zip
cd health-refund-assistant
```

### Passo 2: Leia a Entrada Principal (5 min)
```bash
# Bem-vindo
cat 01_leia_primeiro.md

# Mapa da estrutura
cat docs/00_mapa_estrutura.md

# Checklist de funcionalidades
cat docs/00_checklist_funcionalidades.md
```

### Passo 3: Escolha Seu Perfil e Comece

**Novo Usuário?** (15 min)
```bash
cat docs/10_quickstart/01_comece_aqui.md
```

**Revisor do Projeto?** (1-2h)
```bash
cat docs/60_project/01_caderno_projeto.md
cat docs/50_architecture/01_visao_geral.md
```

**Executor (Codespaces)?** (20 min)
```bash
cat docs/40_testing/03_verificacao_codespaces_ui.md
python app.py
```

**Arquiteto de AI Agent?** (1-2h)
```bash
cat docs/50_architecture/02_ai_agent_architecture.md
cat docs/70_documentation/06_casos_teste_memory.md
```

**Apresentador (Grupo)?** (30 min)
```bash
cat docs/60_project/02_apresentacao_grupo.md
cat docs/40_testing/01_checklist_entrega.md
```

---

## 📂 Estrutura Rápida

```
01_leia_primeiro.md ..................... COMECE AQUI
02_copilot_guidelines.md ................ Diretrizes permanentes
README.md ............................... GitHub

docs/00_mapa_estrutura.md ............... HUB CENTRAL (navegação)
docs/00_checklist_funcionalidades.md ... Verificação 100%

docs/10_quickstart/ ..................... Começar rápido
docs/20_process/ ........................ Processos e rastreamento
docs/30_requirements/ ................... Requisitos (R1-R5)
docs/40_testing/ ........................ Testes e checklist
docs/50_architecture/ ................... Arquitetura geral + AI Agent
docs/60_project/ ........................ Projeto formal + Apresentação
docs/70_documentation/ .................. Documentação centralizadad
```

---

## 🛠️ Comandos Essenciais

### Configurar Ambiente
```bash
# Criar virtual env (se não existir)
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux
# ou
.venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt
```

### Rodar Testes
```bash
# Todos os testes
pytest -v

# Ou
python -m unittest discover -s tests -v

# Teste específico
pytest tests/test_vlm_extractor.py -v
```

### Rodar UI (Streamlit)
```bash
python app.py
# Acessa: http://localhost:8501
```

### Gerar Fixtures Sintéticas
```bash
python scripts/gerar_fixtures_sinteticas.py
# Gera C01-C15 PDFs em data/sinteticos/documentos/
```

### Avaliar Casos
```bash
python scripts/case_evaluation_v3.py
# Gera relatório em json/evaluation/reports/
```

---

## 📋 Verificação Rápida

```bash
# 1. Verificar se está limpo (sem cache)
find . -name "__pycache__" -o -name "*.pyc" -o -name ".pytest_cache"
# Deve estar VAZIO

# 2. Verificar padrão snake_case
find docs -name "*.md" | grep -E "[A-Z]"
# Deve estar VAZIO

# 3. Verificar números ordinais
find docs -name "*.md" | grep -v "^docs/[0-9][0-9]_"
# Deve estar VAZIO

# 4. Verificar modelos LLM
grep -r "gpt-4o-mini" --include="*.md" docs/
# Deve estar VAZIO (apenas em .venv é permitido)

grep -r "GPT-6 Luna" --include="*.md" docs/ | head -5
# Deve ter múltiplas referências
```

---

## 🎯 Timeline até 02/12/2026

| Data | Ação | Arquivos |
|---|---|---|
| **Hoje** | Leia documentação, compreenda o projeto | 01_leia_primeiro.md, docs/00_mapa_estrutura.md |
| **Semana 1** | Execute testes via Codespaces | pytest -v |
| **Semana 2** | Rodar UI e testar casos C01-C15 | python app.py |
| **Semana 3** | Preencher planilha de testes | docs/70_documentation/07_planilha_testes_5_casos.md |
| **02/12** | Gerar ZIP final e entregar | `git archive -o final.zip HEAD` |

---

## ❓ Perguntas Comuns

### Q: Por onde começo?
**A:** Leia `01_leia_primeiro.md` → `docs/00_mapa_estrutura.md` → escolha seu perfil

### Q: Como rodar a UI?
**A:** `python app.py` (precisa de OPENAI_API_KEY em .env)

### Q: Como rodar testes?
**A:** `pytest -v` ou `python -m unittest discover -s tests -v`

### Q: O projeto usa GPT-6 Luna?
**A:** ✅ SIM - 100% migrado em 2026-11-25. Grafia correta: **"GPT-6 Luna"**

### Q: Onde estão os dados pessoais?
**A:** ✅ REMOVIDOS (LGPD) - apenas fixtures sintéticas (C01-C15) no Git

### Q: E se precisar adicionar documentação?
**A:** Use padrão: `NN_categoria/MM_nome_arquivo.md` em snake_case

### Q: Como rastrear mudanças do grupo?
**A:** Veja `docs/20_process/01_rastreamento_testes.md` e `02_copilot_guidelines.md`

---

## ✅ Checklist Rápido

Antes de enviar qualquer código/docs:

- [ ] Leu `01_leia_primeiro.md`
- [ ] Entendeu `docs/00_mapa_estrutura.md`
- [ ] Verificou `docs/00_checklist_funcionalidades.md`
- [ ] Testou localmente: `pytest -v`
- [ ] Executou: `python app.py`
- [ ] Verificou padrão: `find docs -name "*.md" | grep -E "[A-Z]"` (vazio?)
- [ ] Commitou com Conventional Commits: `git add` → `git commit -m "type: description"`

---

## 🔗 Links Importantes

| Documento | Propósito |
|---|---|
| [01_leia_primeiro.md](/01_leia_primeiro.md) | Entrada principal |
| [docs/00_mapa_estrutura.md](/docs/00_mapa_estrutura.md) | Navegação centralizada |
| [docs/00_checklist_funcionalidades.md](/docs/00_checklist_funcionalidades.md) | Verificação 100% |
| [docs/00_relatorio_reorganizacao_v2.0.md](/docs/00_relatorio_reorganizacao_v2.0.md) | Relatório completo |
| [docs/60_project/01_caderno_projeto.md](/docs/60_project/01_caderno_projeto.md) | Projeto R1-R5 |
| [docs/60_project/02_apresentacao_grupo.md](/docs/60_project/02_apresentacao_grupo.md) | Apresentação 09/12 |
| [docs/40_testing/01_checklist_entrega.md](/docs/40_testing/01_checklist_entrega.md) | Checklist pré-entrega |

---

## 🎓 Aprenda Mais

- **Arquitetura:** `docs/50_architecture/01_visao_geral.md`
- **AI Agent Design:** `docs/50_architecture/02_ai_agent_architecture.md`
- **Casos de Teste:** `docs/70_documentation/07_planilha_testes_5_casos.md`
- **Padrões & Diretrizes:** `02_copilot_guidelines.md`

---

**Pronto? Comece lendo `01_leia_primeiro.md` e `docs/00_mapa_estrutura.md`!**

```
🚀 Projeto v2.0 • 100% Reorganizado • GPT-6 Luna • Pronto para Usar
```
