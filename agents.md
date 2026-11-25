# Copilot Agent Instructions

**Projeto:** health-refund-assistant  
**Versão:** 2.0  
**Data:** 2026-11-25  
**Modelo LLM:** GPT-6 Luna

---

## 🎯 Diretrizes Permanentes para Copilot

Este arquivo define as regras que **TODO o Copilot DEVE seguir** automaticamente em qualquer trabalho neste repositório.

---

## 1️⃣ PADRÃO DE NOMENCLATURA

### Arquivos e Pastas
- **OBRIGATÓRIO:** `snake_case` (nomes_compostos_minusculos)
- **OBRIGATÓRIO:** Números ordinais (NN_) para ordenação
  - Raiz: `01_`, `02_`, etc.
  - Categorias: `10_quickstart/`, `20_process/`, etc.
  - Dentro de categorias: `01_`, `02_`, `03_`, etc.
- **NUNCA:** MAIÚSCULA, camelCase, PascalCase, espaços em nomes
- **NUNCA:** Arquivos como `LEIA_PRIMEIRO.md`, `INDEX.md`, `README_ARQUIVO.md`

### Exemplo Correto
```
✅ 01_leia_primeiro.md
✅ 02_copilot_guidelines.md
✅ docs/10_quickstart/01_comece_aqui.md
✅ docs/50_architecture/02_ai_agent_architecture.md
❌ LEIA_PRIMEIRO.md
❌ AI_AGENT_ARCHITECTURE.md
❌ Readme.md
```

---

## 2️⃣ MODELOS LLM

### Modelo Único Obrigatório
- **Grafia EXATA:** `GPT-6 Luna` (nunca `gpt-6-luna`, `GPT-6-LUNA`, `gpt-6 luna`)
- **Em código Python:** Variável `model="gpt-6-luna"` (string lowercase)
- **Em documentação:** Sempre `GPT-6 Luna` (título case)

### Temperatura e Top P (por tarefa)
```
Análise/Review:       temperature=0.3, top_p=0.9    (máxima precisão)
Revisão de código:    temperature=0.3, top_p=0.9    (máxima precisão)
Implementação:        temperature=0.5, top_p=0.8    (equilíbrio)
Design/Arquitetura:   temperature=0.7, top_p=0.95   (exploração)
Testes:               temperature=0.3, top_p=0.9    (máxima precisão)
Documentação:         temperature=0.4, top_p=0.85   (clareza + estrutura)
```

### Validação
- [ ] Verificar se está usando `GPT-6 Luna` em TODOS os documentos
- [ ] Verificar se temperatura/top_p correspondem à tarefa
- Comando: `grep -r "gpt-4o-mini" docs/ && echo "⚠️ ATUALIZAR"`

---

## 3️⃣ ORDEM DE LEITURA (5 PERFIS)

Quando um usuário começa no projeto, dirija-o para:

### Novo Usuário (15 min)
1. `01_leia_primeiro.md`
2. `docs/00_guia_rapido_inicio.md`
3. `docs/00_mapa_estrutura.md`
4. Depois: `docs/10_quickstart/01_comece_aqui.md`

### Revisor (1-2h)
1. `01_leia_primeiro.md`
2. `02_copilot_guidelines.md`
3. `docs/00_mapa_estrutura.md`
4. `docs/60_project/01_caderno_projeto.md`
5. `docs/50_architecture/01_visao_geral.md`

### Executor Codespaces (20 min)
1. `docs/00_guia_rapido_inicio.md`
2. `docs/40_testing/03_verificacao_codespaces_ui.md`
3. `docs/70_documentation/10_status_codespaces.md`

### Arquiteto AI Agent (1-2h)
1. `02_copilot_guidelines.md`
2. `docs/50_architecture/02_ai_agent_architecture.md`
3. `docs/50_architecture/03_extension_arquitetura.md`
4. `docs/70_documentation/06_casos_teste_memory.md`

### Apresentador Grupo (30 min)
1. `docs/60_project/02_apresentacao_grupo.md`
2. `docs/60_project/01_caderno_projeto.md`
3. `docs/40_testing/01_checklist_entrega.md`

---

## 4️⃣ ESTRUTURA DE DOCUMENTAÇÃO

### Categorias Obrigatórias
```
docs/
├── 10_quickstart/          Começar rápido (20 min)
├── 20_process/             Processos e rastreamento
├── 30_requirements/        Requisitos (R1-R5)
├── 40_testing/             Testes e checklist
├── 50_architecture/        Arquitetura geral + AI Agent + Extension
├── 60_project/             Projeto formal + Apresentação + Roadmap
└── 70_documentation/       Documentação centralizada
```

### Documentos Centrais (00_*.md)
- `00_mapa_estrutura.md` — Hub de navegação
- `00_guia_rapido_inicio.md` — 3 Passos para começar
- `00_checklist_funcionalidades.md` — Verificação 100%
- `00_relatorio_reorganizacao_v2.0.md` — Relatório completo
- `00_audit_consistencia.md` — Auditoria de inconsistências

---

## 5️⃣ PADRÃO DE BRANCHES (Grupo)

### Nomenclatura
```
feature/usuario_nome/descricao
fix/usuario_nome/descricao
docs/usuario_nome/descricao
```

Exemplo: `feature/fernando/ai-agent-memory-isolation`

### Checklist Pré-Merge
- [ ] Nome segue padrão: `feature/nome/descricao`
- [ ] CHANGELOG_BRANCH.md preenchido
- [ ] TEST_EXECUTION_LOG.csv atualizado
- [ ] Arquivos em snake_case + ordinais
- [ ] Modelos LLM = "GPT-6 Luna"
- [ ] Testes passam: `pytest -v`
- [ ] Sem .pyc, cache, .DS_Store

---

## 6️⃣ RASTREAMENTO DE TESTES (Grupo)

### Arquivo: TEST_EXECUTION_LOG.csv
```csv
data,hora,usuario,teste,metodo,resultado,tempo_segundos
2026-11-25,19:50,fernando,test_vlm_extractor,pytest,PASS,2.3
2026-11-25,19:51,fernando,test_assessment,pytest,PASS,1.8
```

### Arquivo: CHANGELOG_BRANCH.md (cada branch)
```
# CHANGELOG - feature/fernando/ai-agent

## 2026-11-25 19:50 - Fernando
- Implementar memory isolation no AI Agent
- Status: IN_PROGRESS
- Testes: test_memory_isolation.py PASS

## 2026-11-25 20:00 - Fernando
- Finalizar documentação
- Status: READY_FOR_REVIEW
- Testes: 11/11 PASS
```

---

## 7️⃣ INSTRUÇÕES PARA CHECKPOINTS/SAVE

Quando salvando checkpoint ou fazendo commit:

1. **Nomenclatura do checkpoint:**
   - Use números ordinais e datas
   - Exemplo: `013-padrão-snake_case-diretrizes-auditor...`

2. **Mensagem de commit (Conventional Commits):**
   ```
   type(scope): description
   
   - Ponto 1
   - Ponto 2
   
   Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
   ```

3. **Tipos:** `feat`, `fix`, `docs`, `refactor`, `build`, `test`, `chore`

---

## 8️⃣ VALIDAÇÃO AUTOMÁTICA

Execute ANTES de qualquer commit:

```bash
# 1. Verificar snake_case
find docs -name "*.md" | grep -E "[A-Z]" && echo "⚠️ MAIÚSCULA ENCONTRADA"

# 2. Verificar números ordinais
find docs -name "*.md" | grep -v "^docs/[0-9][0-9]_" && echo "⚠️ SEM ORDINAIS"

# 3. Verificar modelos LLM
grep -r "gpt-4o-mini" docs/ && echo "⚠️ ATUALIZAR PARA GPT-6 Luna"
grep -r "gpt-6-luna" docs/ && echo "⚠️ USE 'GPT-6 Luna' em docs"

# 4. Verificar lixo
find . -name "__pycache__" -o -name "*.pyc" -o -name ".pytest_cache"

# 5. Testes
pytest -v
```

---

## 9️⃣ DOCUMENTOS ESTRATÉGICOS

| Documento | Propósito | Localização |
|---|---|---|
| `01_leia_primeiro.md` | Entrada do projeto | Raiz |
| `02_copilot_guidelines.md` | Diretrizes permanentes | Raiz |
| `docs/00_mapa_estrutura.md` | Hub de navegação | docs/ |
| `docs/00_guia_rapido_inicio.md` | 3 Passos para começar | docs/ |
| `docs/60_project/01_caderno_projeto.md` | Projeto R1-R5 formal | docs/60_project/ |
| `docs/60_project/02_apresentacao_grupo.md` | Apresentação 09/12 | docs/60_project/ |
| `docs/40_testing/01_checklist_entrega.md` | Checklist pré-entrega | docs/40_testing/ |

---

## 🔟 HISTÓRICO DE VERSÕES

| Data | Versão | Mudanças | Responsável |
|---|---|---|---|
| 2026-11-25 | 2.0 | Reorganização completa + GPT-6 Luna | Copilot |
| 2026-11-24 | 1.1 | Diretrizes iniciais | Copilot |
| 2026-11-23 | 1.0 | Criação | Copilot |

---

## 📌 RESUMO RÁPIDO

**Ao começar QUALQUER tarefa neste projeto:**

1. ✅ Leia `01_leia_primeiro.md` + `docs/00_mapa_estrutura.md`
2. ✅ Use SEMPRE: `snake_case` + `NN_ordinais`
3. ✅ Use SEMPRE: `"GPT-6 Luna"` (nunca gpt-4o-mini)
4. ✅ Coloque markdown em: `docs/NN_categoria/MM_nome.md`
5. ✅ Execute: `pytest -v` antes de commit
6. ✅ Valide: `grep -r "gpt-4o-mini" docs/` (deve estar vazio)
7. ✅ Commit: `git commit -m "type: description"` (Conventional)
8. ✅ Branch: `feature/nome/descricao`

---

**Este arquivo é a autoridade final para padrões de projeto.** Consulte-o sempre que tiver dúvidas.

---

**Última atualização:** 2026-11-25  
**Vigente até:** 2026-12-31 (próxima revisão esperada)
