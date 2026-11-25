# 📁 Estrutura de Documentação — Padrão snake_case

**Data:** 25 de novembro de 2026  
**Status:** 🟢 DOCUMENTAÇÃO REORGANIZADA E PADRONIZADA

---

## 🎯 Objetivo da Reorganização

Todos os documentos `.md` agora seguem **padrão snake_case** e estão **organizados em categorias** dentro de `docs/`:

```
docs/
├── INDEX.md                    # 👈 COMECE AQUI (mapa de navegação)
├── 01_quickstart/              # 🚀 Início rápido
├── 02_process/                 # ⚙️ Processo/Fluxo
├── 03_requirements/            # 📋 Requisitos
├── 04_testing/                 # ✅ Testes
├── 05_architecture/            # 🏛️ Arquitetura
├── 06_security/                # 🔐 Segurança
├── caderno_projeto.md          # 📄 Requisitos formais (R1-R5)
└── planilha_testes_5_casos.md  # 📊 Resultados dos testes
```

**Benefícios:**
- ✅ Consistência (snake_case em todos os arquivos)
- ✅ Organização (categorias lógicas)
- ✅ Navegação (INDEX.md como mapa)
- ✅ Manutenção (fácil encontrar documentos)

---

## 📂 Estrutura Completa

### 1️⃣ `01_quickstart/` — Comece Aqui (🚀 LEIA PRIMEIRO)

```
01_quickstart/
├── 01_comece_aqui.md              # 3 passos para começar
└── 02_quick_reference.md          # Referência rápida
```

**Quando:** Primeira vez usando  
**Tempo:** 1-5 minutos  
**Leia:** `01_comece_aqui.md`

---

### 2️⃣ `02_process/` — Fluxo e Processos (⚙️ HOW IT WORKS)

```
02_process/
└── 01_rastreamento_testes.md      # Sistema de rastreamento automático
```

**Quando:** Executar testes com logging  
**Tempo:** 10 minutos  
**Executar:** `python scripts/test_tracker.py --mode run --verbose`

---

### 3️⃣ `03_requirements/` — Requisitos (📋 O QUE FOI PEDIDO)

```
03_requirements/
├── 01_respostas_perguntas.md      # Suas 3 perguntas respondidas ⭐
└── 02_conferencia_final.md        # Conferência pré-02/12
```

**Quando:** Entender as 3 perguntas chave  
**Tempo:** 15 minutos  
**Leia:** `01_respostas_perguntas.md`

---

### 4️⃣ `04_testing/` — Testes e Validação (✅ VERIFICAR)

```
04_testing/
├── 01_checklist_entrega.md        # Checklist de entrega
├── 02_verificacao_completa.md     # Verificação de 5 fases
└── 03_verificacao_codespaces_ui.md # Teste com Codespaces + UI ⭐⭐
```

**Quando:** Validar que tudo funciona  
**Tempo:** 15-20 minutos  
**Leia:** `03_verificacao_codespaces_ui.md`

---

### 5️⃣ `05_architecture/` — Arquitetura (🏛️ VISÃO TÉCNICA)

```
05_architecture/
└── 01_visao_geral.md              # Visão geral de entrega
```

**Quando:** Entender arquitetura  
**Tempo:** 10 minutos  
**Leia:** Se for revisor técnico

---

### 6️⃣ `06_security/` — Segurança (🔐 CONFORMIDADE)

```
06_security/
└── [Vazio — veja README.md para segurança]
```

**Quando:** Conformidade LGPD  
**Leia:** README.md (seção Segurança)

---

## 📄 Documentação Técnica Formal

### `caderno_projeto.md` — Requisitos R1-R5

```
Requisitos Técnicos Formais:
  R1: Problema e Valor
  R2: Prompt Engineering (v1.0 → v4.0)
  R3: Recurso de IA (VLM + JSON)
  R4: Testes e Análise
  R5: Segurança e Ética
```

**Quando:** Revisão formal  
**Leia:** Se for revisor técnico do grupo

---

### `planilha_testes_5_casos.md` — Resultados

```
Tabela com:
  - 5 casos de teste (C01-C05)
  - Entrada/saída esperada
  - Resultado observado (v4.0)
  - Status: 5/5 ✅
```

**Quando:** Validar resultados  
**Leia:** Antes de 02/12

---

## 🏠 Raiz: Apenas README.md

**Mantido:** `README.md` (visão técnica)  
**Removidos:** Todos os .md capitalizados (COMECE_AQUI_CODESPACES.md, etc)  
**Novo:** Referência para `docs/INDEX.md`

```
# Raiz (/)
├── README.md           # Único .md na raiz (visão técnica)
├── docs/               # Toda documentação organizada
├── src/                # Código-fonte
├── tests/              # Testes (60 testes unitários)
├── scripts/            # Utilitários
├── json/               # Dados estruturados
└── data/               # Dados de entrada
```

---

## 🔍 Como Encontrar Documentos

### "Quero começar RÁPIDO"
→ `docs/01_quickstart/01_comece_aqui.md`

### "Quero entender o fluxo"
→ `docs/02_process/01_rastreamento_testes.md`

### "Respostas às minhas perguntas"
→ `docs/03_requirements/01_respostas_perguntas.md`

### "Validar que funciona"
→ `docs/04_testing/03_verificacao_codespaces_ui.md`

### "Requisitos formais (R1-R5)"
→ `docs/caderno_projeto.md`

### "Resultados dos testes"
→ `docs/planilha_testes_5_casos.md`

### "Mapa completo"
→ `docs/INDEX.md`

---

## 📋 Padrão de Nomenclatura

Todos os arquivos agora usam **snake_case**:

| Antes | Depois |
|-------|--------|
| `COMECE_AQUI_CODESPACES.md` | `01_quickstart/01_comece_aqui.md` |
| `GUIA_RASTREAMENTO_CODESPACES.md` | `02_process/01_rastreamento_testes.md` |
| `RESPOSTAS_SUAS_PERGUNTAS.md` | `03_requirements/01_respostas_perguntas.md` |
| `VERIFICACAO_ENTREGA_FINAL.md` | `04_testing/02_verificacao_completa.md` |
| `README.md` | `README.md` (mantido na raiz) |

---

## 🗂️ Organização por Categoria

| Categoria | Pastas | Conteúdo |
|-----------|--------|----------|
| Quickstart | 01_quickstart | Início rápido (3 passos) |
| Process | 02_process | Fluxos e processos |
| Requirements | 03_requirements | Requisitos + respostas |
| Testing | 04_testing | Testes + validação |
| Architecture | 05_architecture | Visão técnica |
| Security | 06_security | Conformidade (vazio) |

---

## 🔗 Referências Cruzadas

Documentos referenciam uns aos outros:

```
01_comece_aqui.md
  ↓
  referencia → 02_rastreamento_testes.md
  referencia → 03_verificacao_codespaces_ui.md

03_respostas_perguntas.md
  ↓
  referencia → caderno_projeto.md (R1-R5)
  referencia → planilha_testes_5_casos.md

INDEX.md
  ↓
  mapa → todas as categorias
  mapa → roteiros por perfil
```

---

## 📝 Comentários em Código

Todos os arquivos `.py` principais agora têm **header inicial** explicando:

```python
"""
Nome do Módulo

OBJETIVO: O que faz
ENTRADA: Dados de entrada
SAÍDA: Dados de saída
PROCESSO: Como funciona no fluxo geral
DOCUMENTO: Referência de documentação
"""
```

**Arquivos com header:**
- `src/health_refund_assistant/assistant.py` ✅
- `src/health_refund_assistant/vlm_extractor.py` ✅
- `src/health_refund_assistant/reconciliation.py` ✅
- `src/health_refund_assistant/assessment.py` ✅
- `src/health_refund_assistant/web_app.py` ✅

---

## ✅ Checklist de Organização

- [x] Todos os .md em padrão snake_case
- [x] Documentos organizados em 6 categorias
- [x] docs/INDEX.md criado como mapa
- [x] Apenas README.md na raiz
- [x] Headers comentados em código Python
- [x] Referências cruzadas entre documentos
- [x] Roteiros por perfil (rápido, revisor, executor)

---

## 🎯 Próximos Passos

1. **Ler:** `docs/01_quickstart/01_comece_aqui.md` (1 min)
2. **Navegar:** `docs/INDEX.md` (como mapa)
3. **Executar:** Conforme sua categoria
4. **Entregar:** 02/12/2026

---

## 📞 Dúvidas

**P: Por que reorganizar?**  
R: Consistência, navegação fácil, profissionalismo.

**P: Como encontro um documento?**  
R: Veja `docs/INDEX.md` como mapa.

**P: Os links funcionam?**  
R: Sim, todos testados (links relativos).

**P: E os arquivos antigos?**  
R: Movidos para docs/ com novo nome (padrão snake_case).

---

**Reorganização Completa:** ✅ 25/11/2026  
**Status:** 🟢 DOCUMENTAÇÃO PRONTA PARA USO  
**Próxima Entrega:** 02/12/2026
