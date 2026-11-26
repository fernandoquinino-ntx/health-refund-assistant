# Copilot Agent Instructions

**Projeto:** health-refund-assistant  
**Versão:** 2.0  
**Data:** 2026-11-25  
**Modelo LLM:** GPT-6 Luna

---

## 🎯 Diretrizes Permanentes para Copilot

Este arquivo define as regras que **TODO o Copilot DEVE seguir** automaticamente em qualquer trabalho neste repositório.

---

## Organização e manutenção contínua

- Mantenha este arquivo e `.github/copilot-instructions.md` alinhados quando o
  usuário estabelecer ou alterar padrões para este repositório. Atualize também
  os índices e a documentação diretamente afetada por mudanças de estrutura.
- Mantenha `docs/60_project/04_changelog_projeto.md` atualizado em cada alteração
  relevante, inicialmente em **Não lançado**. Siga a política SemVer registrada
  ali; não invente releases, tags, datas ou resultados de testes.
- Mantenha a aplicação em `src/health_refund_assistant/`: módulos compartilhados
  em `core/`, tarefas em `conversation/`, documentos em `documents/`, plano em
  `plan/` e interface em `web/`. `app.py` é o ponto de entrada; testes ficam em
  `tests/` e ferramentas de avaliação em `scripts/`, não no núcleo.
- Inicie cada arquivo de código com uma descrição breve do que faz e da etapa do
  processo, usando a forma apropriada da linguagem, como docstring em Python.
- JSONs ficam em `json/` por processo; registre caminhos em `core/paths.py` e
  documente contratos ao lado dos schemas. Os prompts versionados ficam em
  `prompts/`: não sobrescreva versões históricas. O Python carrega o prompt e o
  schema correspondente, gera o modelo JSON e valida a resposta.
- Defina tarefas de IA com entrada, saída, guardrails e conferência. Não trate
  validação de schema como prova de verdade, segurança, pagamento ou elegibilidade.
- Não afirme que API, modelo, Codespaces, testes ou resultados reais foram
  verificados sem executá-los. Nunca invente saídas, relatórios ou logs de testes.
  Não versione credenciais, exportações pessoais ou memória de conversas.
- A extensão carregável está em `extension/`; `src/extension/` ainda precisa de
  ajustes antes de substituir a versão carregável. Não apague nenhuma das duas
  sem validar a substituta e preservar o comportamento.

---

## 1️⃣ PADRÃO DE NOMENCLATURA

### Arquivos e Pastas
- **OBRIGATÓRIO:** `snake_case` (nomes_compostos_minusculos)
- **DOCUMENTAÇÃO:** Números ordinais (NN_) para ordenação
  - Documentos gerais ficam em `docs/`, por categoria, com índice e ordem de leitura.
  - Categorias: `10_quickstart/`, `20_process/`, etc.
  - Dentro de categorias: `01_`, `02_`, `03_`, etc.
- **PYTHON:** `snake_case` sem prefixos numéricos em módulos e pacotes.
- **EXCEÇÕES:** `README.md`, arquivos de instrução do agente e nomes exigidos por
  ferramentas, como `.github/copilot-instructions.md` e `manifest.json`.
- **NUNCA:** camelCase, PascalCase ou espaços nos demais nomes
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
- [ ] Identificar o modelo configurado sem alterar registros históricos de outros modelos
- [ ] Verificar se temperatura/top_p correspondem à tarefa
- Os parâmetros dependem da API e da tarefa; consulte o código e a compatibilidade
  do modelo antes de afirmar que estão ativos. Eles não garantem privacidade.
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
- [ ] Changelog do projeto atualizado
- [ ] TEST_EXECUTION_LOG.csv atualizado
- [ ] Arquivos em snake_case + ordinais
- [ ] Modelos LLM = "GPT-6 Luna"
- [ ] Testes passam: `.venv/bin/python -m unittest discover -s tests -v`
- [ ] Sem .pyc, cache, .DS_Store

---

## 6️⃣ RASTREAMENTO DE TESTES (Grupo)

### Arquivo: TEST_EXECUTION_LOG.csv
Exemplo de formato, não resultados reais:
```csv
data,hora,usuario,teste,metodo,resultado,tempo_segundos
2026-11-25,19:50,fernando,test_vlm_extractor,pytest,PASS,2.3
2026-11-25,19:51,fernando,test_assessment,pytest,PASS,1.8
```

### Changelog do projeto

Registre alterações em `docs/60_project/04_changelog_projeto.md`, na seção
**Não lançado**, e siga sua política SemVer. Um registro por branch não é
criado automaticamente.

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
.venv/bin/python -m unittest discover -s tests -v
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
5. ✅ Execute: `.venv/bin/python -m unittest discover -s tests -v` antes de commit
6. ✅ Valide: `grep -r "gpt-4o-mini" docs/` (deve estar vazio)
7. ✅ Commit: `git commit -m "type: description"` (Conventional)
8. ✅ Branch: `feature/nome/descricao`

---

**Este arquivo é a autoridade final para padrões de projeto.** Consulte-o sempre que tiver dúvidas.

---

**Última atualização:** 2026-11-25  
**Revisão:** atualizar quando as preferências ou a estrutura do projeto mudarem.
