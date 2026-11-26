# 🤖 Copilot Guidelines - Health Refund Assistant

**Data de Criação:** 25/11/2026  
**Versão:** 1.0  
**Escopo:** Diretrizes permanentes para qualquer trabalho neste repositório

---

## 1️⃣ PADRÕES DE NOMENCLATURA

### Arquivos Markdown
- ✅ **OBRIGATÓRIO:** `snake_case` com extensão `.md`
- ❌ **PROIBIDO:** CamelCase, SCREAMING_SNAKE_CASE, ou espaços
- ✅ **EXEMPLOS:**
  - `leia_primeiro.md` ✅
  - `ai_agent_architecture.md` ✅
  - `resumo_executivo_ai_agent.md` ✅
  - `casos_teste_memory_isolation.md` ✅
  - `LEIA_PRIMEIRO.md` ❌
  - `AI_AGENT_ARCHITECTURE.md` ❌

### Arquivos Python
- ✅ **OBRIGATÓRIO:** `snake_case` com extensão `.py`
- ✅ **EXEMPLOS:**
  - `vlm_extractor.py` ✅
  - `test_tracker.py` ✅
  - `gerar_fixtures_sinteticas.py` ✅

### Pastas
- ✅ **OBRIGATÓRIO:** `snake_case` sem underscore inicial
- ✅ **EXEMPLOS:**
  - `docs/` ✅
  - `src/` ✅
  - `json/schemas/` ✅
  - `data/sinteticos/` ✅

### Variáveis Git
- ✅ **BRANCH:** `feature/nome_descritivo` ou `bugfix/descricao`
- ✅ **COMMITS:** Padrão Conventional Commits
  ```
  type(scope): descrição
  
  Exemplo:
  docs: Renomear arquivos para snake_case
  feat(memory): Implementar sistema de memória por usuário
  fix(test): Corrigir case de isolamento de dados
  ```

---

## 2️⃣ CONFIGURAÇÃO DE MODELOS LLM

### Temperatura e Top P
```json
{
  "modelo_padrao": "GPT-6 Luna",
  "temperatura": {
    "analise_tecnica": 0.3,
    "criacao_codigo": 0.5,
    "documentacao": 0.4,
    "brainstorm_arquitetura": 0.7
  },
  "top_p": {
    "analise_tecnica": 0.9,
    "criacao_codigo": 0.8,
    "documentacao": 0.85,
    "brainstorm_arquitetura": 0.95
  }
}
```

### Modelos por Tarefa
| Tarefa | Modelo | Temperatura | Top P | Motivo |
|--------|--------|-------------|-------|--------|
| Revisão código | GPT-6 Luna | 0.3 | 0.9 | Precisão máxima |
| Escrita documentação | GPT-6 Luna | 0.4 | 0.85 | Clareza + estrutura |
| Implementação | GPT-6 Luna | 0.5 | 0.8 | Equilíbrio criatividade/precisão |
| Design arquitetura | GPT-6 Luna | 0.7 | 0.95 | Exploração de ideias |
| Testes | GPT-6 Luna | 0.3 | 0.9 | Precisão em casos |

---

## 3️⃣ ORDEM DE LEITURA DOS DOCUMENTOS

### Para Novo Usuário (15 minutos)
1. `leia_primeiro.md` — Guia de acesso rápido
2. `docs/01_quickstart/01_comece_aqui.md` — 3 passos iniciais
3. `docs/index.md` — Mapa de navegação

### Para Revisor Técnico (1-2 horas)
1. `docs/caderno_projeto.md` — Projeto formal (R1-R5)
2. `docs/planilha_testes_5_casos.md` — Resultados esperados
3. `docs/resumo_executivo_ai_agent.md` — Evolução futura
4. `docs/ai_agent_architecture.md` — Arquitetura completa

### Para Executor (Codespaces, 20 minutos)
1. `leia_primeiro.md` — Guia rápido
2. `docs/00_status_codespaces.md` — Setup Codespaces
3. `docs/04_testing/03_verificacao_codespaces_ui.md` — Validação 5 casos

### Para Arquiteto AI Agent (1-2 horas)
1. `docs/resumo_executivo_ai_agent.md` — Visão geral (5 min)
2. `docs/ai_agent_architecture.md` — Arquitetura completa (20 min)
3. `docs/casos_teste_memory_isolation.md` — 15 casos teste (15 min)
4. `docs/roadmap_ai_agent.md` — 5 fases timeline (10 min)

### Para Apresentação Grupo (30-45 minutos)
1. `docs/apresentacao_grupo.md` — Script completo
2. `docs/resumo_executivo_ai_agent.md` — Referência rápida
3. Demo ao vivo no Codespaces (C01 caso pago)

---

## 4️⃣ VERIFICAÇÃO DE CONSISTÊNCIA

### Regras de Ouro
✅ **Fazer:**
- Um documento referencia outro? Use links relativos `[texto](../caminho/arquivo.md)`
- Versão de modelo mencionada? Use EXATAMENTE: `GPT-6 Luna` (não `GPT-6 Luna`, não `GPT-6-LUNA`)
- Data mencionada? Use formato ISO: `2026-11-25`
- Número de caso? Use EXATAMENTE: `C01`, `C02`, ..., `C15` (não `C1`, não `caso_01`)

❌ **Nunca:**
- Dois documentos com informações conflitantes sobre a mesma coisa
- Referências a arquivos que não existem
- Modelos mencionados com grafia inconsistente
- Datas em formatos diferentes
- Versões de código desatualizadas sem atualizar documentação

### Checklist de Consistência
Ao criar/editar um documento, verificar:
- [ ] Padrão de nomenclatura: snake_case
- [ ] Referências cruzadas: links corretos
- [ ] Modelos LLM: sempre `GPT-6 Luna`
- [ ] Versões: v1.0, v2.0, v3.0, v4.0 (consistente)
- [ ] Nomes de testes: sempre `C01`-`C15`
- [ ] Datas: sempre ISO 8601 (YYYY-MM-DD)
- [ ] Nenhuma duplicação de informação em múltiplos docs

---

## 5️⃣ RASTREAMENTO PARA O GRUPO

### Padrão de Branch
```
feature/usuario_nome/descricao_trabalho
  ├── feature/fernando/fase_1_memory_system
  ├── feature/joao/testes_cases_c01_c05
  └── feature/maria/documentacao_seguranca
```

### Changelog e versões
Registre alterações relevantes em
[`docs/60_project/04_changelog_projeto.md`](./docs/60_project/04_changelog_projeto.md),
na seção **Não lançado**, e siga a política SemVer documentada. Não há changelog
por branch criado automaticamente; não invente releases, tags ou resultados.

### Rastreamento de Testes
Criar `TEST_EXECUTION_LOG.csv`:
```csv
data,hora,usuario,teste,metodo,resultado,observacao,tempo_segundos
2026-11-25,19:30,fernando,C01,ui,passou,Nota paga integralmente,45
2026-11-25,19:35,fernando,C02,ui,passou,Nota com glosa,52
2026-11-25,19:40,joao,C03,script,falhou,Validação PIN,erro_timeout
2026-11-25,20:00,joao,C03,script,passou,Retry bem-sucedido,38
```

### Report Final
Após conclusão de cada fase, gerar `REPORT_FASE_X.md`:
```markdown
# Report - Fase 1: Core Foundation

**Data de Início:** 2026-12-16
**Data de Conclusão:** 2027-01-02
**Responsáveis:** Fernando, João

## Entregas
- ✅ knowledge.py
- ✅ memory.py
- ✅ auth/

## Testes
- C01-C09: 9/9 passando (100%)

## Issues Resolvidas
- #12: Memory persist após desconexão
- #15: PIN validation com bcrypt

## Pendências para Fase 2
- ...
```

---

## 6️⃣ PROCESSO DE REVISÃO DE DOCUMENTOS

### Checklist Antes de Merge
- [ ] Todos os arquivos em `snake_case`
- [ ] Nenhum link quebrado (verificar com `grep`)
- [ ] Modelos LLM com grafia consistente
- [ ] Versões de código atualizadas
- [ ] Datas em ISO 8601
- [ ] Nomes de testes (C01-C15) consistentes
- [ ] Nenhuma duplicação de informação
- [ ] Tabelas formatadas corretamente
- [ ] Código-exemplo com sintaxe correta
- [ ] Nenhuma informação sensível (chaves, senhas, dados pessoais)

### Validação Automática
Execute antes de fazer push:
```bash
# Verificar snake_case
find docs -name "*.md" | grep -E "[A-Z]" && echo "❌ Arquivos com MAIÚSCULA!" || echo "✅ Todos em snake_case"

# Verificar links
grep -r "](\.\./" docs/ | head -5

# Verificar modelos
grep -r "gpt-6" docs/ && echo "⚠️ Verificar grafia (use GPT-6 Luna)"

# Verificar casos de teste
grep -r "C0" docs/ | grep -v "C01\|C02\|C03\|C04\|C05\|C06\|C07\|C08\|C09\|C10\|C11\|C12\|C13\|C14\|C15" && echo "⚠️ Nomeclatura de caso incorreta"
```

---

## 7️⃣ INSTRUÇÕES PARA PRÓXIMOS CHECKPOINTS

### Ao Iniciar Trabalho
1. Criar branch com seu nome: `feature/nome_usuario/descricao`
2. Registrar mudanças relevantes no changelog do projeto em **Não lançado**
3. Criar `TEST_EXECUTION_LOG.csv` conforme executa testes
4. Manter `docs/index.md` atualizado com suas mudanças

### Ao Finalizar Trabalho
1. Verificar TODOS os pontos da seção 6️⃣ (Checklist)
2. Executar validação automática
3. Criar `REPORT_FASE_X.md`
4. Fazer PR com referência a branch + changelog
5. Atualizar `docs/index.md` com entregas finais

### Comunicação com Grupo
- Atualizar `TEST_EXECUTION_LOG.csv` DURANTE o trabalho (não depois)
- Manter o changelog do projeto atualizado conforme mudanças relevantes
- Gerar `REPORT_FASE_X.md` ao finalizar fase

---

## 8️⃣ REFERÊNCIA RÁPIDA

| Padrão | Exemplo | Checklist |
|--------|---------|-----------|
| Arquivo markdown | `resumo_executivo_ai_agent.md` | ✅ snake_case |
| Arquivo Python | `vlm_extractor.py` | ✅ snake_case |
| Pasta | `docs/01_quickstart/` | ✅ snake_case |
| Branch | `feature/fernando/fase_1_memory` | ✅ descritivo |
| Modelo | `GPT-6 Luna` | ✅ EXATAMENTE assim |
| Versão | `v1.0`, `v2.0`, `v3.0`, `v4.0` | ✅ consistente |
| Teste | `C01`, `C02`, ..., `C15` | ✅ EXATAMENTE assim |
| Data | `2026-11-25` | ✅ ISO 8601 |

---

## 9️⃣ DOCUMENTOS ESTRATÉGICOS (NUNCA EDITAR SEM VALIDAÇÃO)

Estes documentos devem ser editados APENAS após revisão total:
- `docs/caderno_projeto.md` — Projeto formal (R1-R5)
- `docs/ai_agent_architecture.md` — Arquitetura principal
- `docs/roadmap_ai_agent.md` — Timeline e fases
- `docs/index.md` — Mapa de navegação

**Regra:** Se vai alterar, fazer PR com `[REVIEW]` no título.

---

## 🔟 VERSÃO E HISTÓRICO

| Versão | Data | Mudanças |
|--------|------|----------|
| 1.0 | 2026-11-25 | Versão inicial com 10 seções |

**Próxima revisão:** 2026-12-16 (Fase 1)

---

**Criado por:** Copilot  
**Para:** Health Refund Assistant Team  
**Uso:** Permanente (enquanto projeto ativo)

---

## ⚠️ VIOLAÇÕES

Se você encontrar algo que viole essas guidelines, abra uma issue com `[GUIDELINES]` no título ou avise no changelog.

Exemplos:
- `ARQUIVO_COM_MAIUSCULA.md` → Renomear para `arquivo_com_minuscula.md`
- Referência a `GPT-4` em vez de `GPT-6 Luna` → Atualizar documentação
- Dada em formato `11/25/2026` → Converter para `2026-11-25`
- Teste nomeado `C1` em vez de `C01` → Padronizar para `C01`
