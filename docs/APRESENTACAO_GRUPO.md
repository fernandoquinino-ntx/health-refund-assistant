# 🎤 Apresentação Grupo - Health Refund Assistant

**Data:** 02/12/2026  
**Formato:** Discussão Técnica de 30-45 minutos  
**Facilitador:** Fernando Quinino  
**Modelo Usado:** GPT-6 Luna

---

## 📋 Agenda Proposta

### 1️⃣ Abertura (3 minutos)
- **Título:** Assistente de Rastreamento de Reembolsos com IA + Isolamento de Dados
- **Problema:** Notas fiscais dispersas em e-mails/WhatsApp → perda de rastreabilidade
- **Solução:** VLM (gpt-4o-mini*) + Determinístico Python + JSON Exportação Portal
  - *Versão Atual. Será migrado para GPT-6 Luna em Fase 1 (Jan 2027)
- **Status:** ✅ 100% Pronto para Entrega

---

### 2️⃣ Demo Técnica (10 minutos)

#### 🎯 Demonstrar ao Vivo (Codespaces)
```bash
# 1. Abrir Codespaces
GitHub → Code → Codespaces → Create codespace on main

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Rodar testes
python scripts/test_tracker.py --mode run --verbose

# 4. Abrir Web App
streamlit run src/web_app.py

# 5. Submeter 1 caso de teste manualmente
# (Usar formulário da UI para C01: Nota padrão paga)
```

#### ✅ Validação em 3 Etapas (Exibir Logs)
1. **VLM Extraction** → JSON Schema validado
2. **Deterministic Check** → D-2 + 365 dias verificados
3. **LLM Response** → Resposta ancorada em fatos

---

### 3️⃣ Dúvidas Esperadas (12 minutos)

#### ❓ **"Como manter memória de conversas?"**
✅ **Resposta:** Arquivos JSON por usuário em `json/memory/users/{user_id}/`
- Estrutura: `conversation_history.json`, `audit_trail.json`, `preferences.json`
- Isolamento: PIN simples (4-6 dígitos) + path validation rigorosa
- Exemplo: Usuário X nunca acessa dados de Usuário Y

#### ❓ **"Como isso evita vazar dados de outras pessoas?"**
✅ **Resposta:** 3 camadas de proteção
1. **Autenticação:** PIN simples na entrada (LGPD-compliant, sem biometria)
2. **Autorização:** Validação de path `../`, `~`, wildcards bloqueadas
3. **Auditoria:** Log de acesso em `audit_trail.json` por usuário

#### ❓ **"Isso precisa de testes formais?"**
✅ **Resposta:** SIM! 15 casos de teste documentados (C01-C15)
- **C01-C03:** Validação de PIN (correto, incorreto, desconhecido)
- **C04-C05:** Isolamento de dados (cross-user bloqueado, path traversal bloqueado)
- **C06-C07:** Persistência (memória após desconexão)
- **C08-C09:** Auditoria LGPD (logging completo, direito ao esquecimento)
- **C10-C15:** Segurança + Robustez (prompt injection, overflow, concurrent users)

#### ❓ **"Como funciona a Fase 1 (Dez 2026)?"**
✅ **Resposta:** 3 arquivos novos + testes
```
Fase 1 Entregáveis:
├─ src/knowledge.py (Knowledge Base API)
├─ src/memory.py (Memory System)
├─ src/auth/ (PIN validation + bcrypt)
└─ Validação: C01-C03, C06-C08 passando
Timeline: 2-3 semanas
```

---

### 4️⃣ Resumo Executivo (5 minutos)

**Leia:** `docs/RESUMO_EXECUTIVO_AI_AGENT.md` (5 min)

Respostas estruturadas para:
- Arquitetura de Memory System
- Estratégia de User Isolation
- Roadmap de 5 fases (Dez 2026 - Abr 2027)
- Próximos passos imediatos

---

### 5️⃣ Próximas Ações (3 minutos)

**Para o Grupo:**
- [ ] Validar 5 casos no Codespaces
- [ ] Revisar `docs/caderno_projeto.md` (R1-R5)
- [ ] Confirmar timeline Fase 1 (Dez 2026)

**Para Fernando:**
- [ ] Implementar Fase 1 (knowledge.py + memory.py + auth/)
- [ ] Executar 15 casos de teste (C01-C15)
- [ ] Validação final em 02/01/2027

---

## 📂 Documentos Chave para Referência

| Documento | Propósito | Tempo |
|-----------|----------|-------|
| [RESUMO_EXECUTIVO_AI_AGENT.md](./RESUMO_EXECUTIVO_AI_AGENT.md) | 3 dúvidas respondidas | 5 min |
| [AI_AGENT_ARCHITECTURE.md](./AI_AGENT_ARCHITECTURE.md) | Arquitetura técnica completa | 20 min |
| [CASOS_TESTE_MEMORY_ISOLATION.md](./CASOS_TESTE_MEMORY_ISOLATION.md) | 15 casos de teste (C01-C15) | 15 min |
| [ROADMAP_AI_AGENT.md](./ROADMAP_AI_AGENT.md) | 5 fases + timeline | 10 min |
| [caderno_projeto.md](./caderno_projeto.md) | Projeto formal (R1-R5) | 30 min |
| [planilha_testes_5_casos.md](./planilha_testes_5_casos.md) | Resultados dos 5 casos obrigatórios | 10 min |

---

## 🎬 Script da Apresentação

### **Slide 1: Contexto do Problema**
> "Hoje, quando um beneficiário envia uma nota fiscal por e-mail ou WhatsApp para a concierge, ela tem que registrar manualmente no portal do plano de saúde. As notas ficam dispersas, as atualizações ocorrem de forma assíncrona, e perde-se rastreabilidade de quem viu, quem processou, quando foi aprovado."

### **Slide 2: Nossa Solução**
> "Combinamos VLM (visão por IA) + Determinístico Python (regras de negócio) + JSON do Portal (reconciliação). O resultado: em 3 etapas, o sistema diz se foi pago, se foi glosado, se está pendente ou se é auditável pré-envio."

### **Slide 3: Demonstração**
> "Vamos submeter um caso real agora no Codespaces e ver as 3 etapas executando..."

### **Slide 4: Isolamento de Dados**
> "Cada usuário tem um PIN. Nunca um usuário acessa dados de outro. Temos 15 testes que provam isso. E tudo é auditado para LGPD."

### **Slide 5: Próximos Passos**
> "Estamos prontos para a Fase 1: implementar Memory System e Tools em dezembro. Vamos validar com 15 casos de teste completos."

---

## ⌚ Timing de Apresentação

| Seção | Tempo | Responsável |
|-------|-------|-------------|
| Abertura | 3 min | Fernando |
| Demo Codespaces (1 caso) | 10 min | Fernando |
| Dúvidas + Respostas | 12 min | Grupo discute |
| Resumo Executivo | 5 min | Fernando |
| Próximas Ações | 3 min | Grupo alinha |
| **TOTAL** | **~33 min** | — |

---

## 🎯 Métricas de Sucesso da Apresentação

✅ **Compreensão**
- [ ] Grupo entende o problema original
- [ ] Grupo vê como VLM + Determinístico + Portal = solução completa
- [ ] Grupo compreende isolamento de dados

✅ **Confiança**
- [ ] Demo ao vivo mostra sistema funcionando
- [ ] 15 casos de teste criam confiança em qualidade
- [ ] Roadmap claro para Fase 1

✅ **Alinhamento**
- [ ] Grupo concorda com timeline (Dez 2026 - Abr 2027)
- [ ] Grupo valida 5 casos no Codespaces
- [ ] Grupo aprova entrega em 02/12/2026

---

## 📦 Checklist Pré-Apresentação

**24 horas antes:**
- [ ] Testar demo no Codespaces (C01 caso pago)
- [ ] Verificar internet/VPN
- [ ] Ter `OPENAI_API_KEY` configurada no `.env`
- [ ] Ter `git log --oneline -5` acessível

**Na hora:**
- [ ] Abrir Codespaces (5 min antes)
- [ ] Executar `pip install -r requirements.txt`
- [ ] Executar `python scripts/test_tracker.py --mode verify`
- [ ] Ter `docs/RESUMO_EXECUTIVO_AI_AGENT.md` pronto

**Após a apresentação:**
- [ ] Coletar feedback do grupo
- [ ] Registrar próximas ações em `docs/CONFERENCIA_FINAL.md`
- [ ] Iniciar Fase 1 (semana de 09/12/2026)

---

## 🔗 Links Rápidos

**Para Novo (15 min):**
1. docs/INDEX.md
2. docs/01_quickstart/01_comece_aqui.md

**Para Revisor (1h):**
1. docs/caderno_projeto.md
2. docs/planilha_testes_5_casos.md
3. docs/RESUMO_EXECUTIVO_AI_AGENT.md

**Para Executor (20 min em Codespaces):**
1. docs/00_status_codespaces.md
2. docs/04_testing/03_verificacao_codespaces_ui.md
3. python scripts/test_tracker.py

**Para Arquiteto:**
1. docs/AI_AGENT_ARCHITECTURE.md
2. docs/CASOS_TESTE_MEMORY_ISOLATION.md
3. docs/ROADMAP_AI_AGENT.md

---

## 📞 Contato

**Dúvidas antes da apresentação?**
- Leia: `docs/RESUMO_EXECUTIVO_AI_AGENT.md`
- Ou: `docs/01_quickstart/01_comece_aqui.md`

**Algo não funciona?**
- Ver: `docs/00_status_codespaces.md`
- Ou: `docs/04_testing/02_verificacao_completa.md`

---

**Status Final:** ✅ ENTREGA PRONTA  
**Gerado em:** 25/11/2026  
**Versão:** 1.0  
**ZIP:** health-refund-assistant-entrega.zip (633 KB)
