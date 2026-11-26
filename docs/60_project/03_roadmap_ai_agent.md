# Roadmap - AI Agent Project Evolution

> **Visão**: Transformar Health Refund Assistant em AI Agent Profissional com Memory, Knowledge, Tools  
> **Timeline**: Fases Incrementais pós-entrega 02/12/2026

---

## 📅 Fases Propostas

### FASE 1: Core Foundation (Dezembro 2026)
**Objetivo**: Implementar Knowledge + Memory + Auth básicos

#### Arquivos a Criar:
```
src/health_refund_assistant/
├── knowledge.py              # KnowledgeBase class
├── memory.py                 # UserMemory + MemorySystem
└── auth/
    ├── user_validator.py     # Validação com PIN
    ├── access_control.py     # Controle de acesso
    └── data_isolation.py     # Isolamento por usuário

json/knowledge/               # Base de conhecimento
├── plan_exports/
│   └── plano_saude_base.json
├── regulations/
│   └── regras_cobertura.json
└── prompts_metadata/
    └── prompt_registry.json

json/memory/                  # Memória por usuário
├── users/
│   └── _schema.json
└── sessions/
    └── _schema.json
```

#### Implementação:
1. `KnowledgeBase`: Carrega JSON do plano e regras
2. `UserMemory`: Carrega/salva histórico por user_id
3. `UserValidator`: Validação simples com PIN (bcrypt hash)
4. Integração no `assistant.py`

#### Testes (C01-C03, C06-C08):
```bash
pytest tests/test_user_validation.py -v
pytest tests/test_memory_persistence.py -v
```

#### Entregável:
- ✅ Código funcional
- ✅ Testes básicos passando
- ✅ Documentação API

---

### FASE 2: Tools Registry (Janeiro 2027)
**Objetivo**: Implementar sistema de ferramentas (Tools)

#### Arquivos a Criar:
```
src/health_refund_assistant/tools/
├── __init__.py               # ToolRegistry
├── base_tool.py              # BaseTool interface
├── vlm_tool.py               # Extração VLM
├── reconciliation_tool.py    # Reconciliação D-2
├── audit_tool.py             # Auditoria pré-envio
├── plan_lookup_tool.py       # Consulta plano
└── history_tool.py           # Histórico do usuário

src/health_refund_assistant/
└── orchestrator.py           # Orquestrador central
```

#### Implementação:
```python
class ToolRegistry:
    tools = {
        "vlm_extract": VLMTool(),
        "reconcile": ReconciliationTool(),
        "audit": AuditTool(),
        "lookup_plan": PlanLookupTool(),
        "get_history": HistoryTool(),
    }
    
    @staticmethod
    def execute(tool_name: str, user_id: str, **kwargs):
        """Executa ferramenta com isolamento de usuário"""
        # Valida que user_id só acessa seus dados
        return ToolRegistry.tools[tool_name].execute(user_id, **kwargs)
```

#### Testes (C10-C11):
```bash
pytest tests/test_tools.py -v
pytest tests/test_llm_memory_injection.py -v
```

#### Entregável:
- ✅ 5 tools implementados
- ✅ Integração com assistant.py
- ✅ Testes de tools

---

### FASE 3: Prompt v4.0 Com Memory (Fevereiro 2027)
**Objetivo**: Atualizar prompt para usar memory + knowledge + tools

#### Arquivos a Atualizar:
```
prompts/reembolso_assistente/
├── v1.0.md (histórico)
├── v2.0.md (histórico)
├── v3.0.md (histórico)
└── v4.0.md (NOVO - com memory + tools + knowledge)
```

#### Prompt v4.0 Template:
```
# SYSTEM INSTRUCTIONS v4.0 - AI Agent with Memory

## USER CONTEXT
Name: {user_name}
Session ID: {session_id}
Previous Interactions: {memory_count}
Trust Level: {trust_level} (new/returning/trusted)

## AVAILABLE KNOWLEDGE
Plan Rules: {plan_rules}
Coverage Limits: {coverage_limits}
Processing Timeline: D-2 cutoff rule
Statute: {statute_summary}

## CONVERSATION HISTORY (Last 5)
{memory_context_window}

## AVAILABLE TOOLS
1. vlm_extract(invoice_pdf) → structured_data
2. reconcile(invoice_data) → reconciliation_result
3. audit(invoice_data) → audit_result
4. lookup_plan(patient_id, service_type) → plan_data
5. get_history(user_id) → conversation_history

## INSTRUCTIONS
- Always greet returning users by name and reference prior interactions
- Use knowledge base for facts
- Call tools when appropriate
- Cite sources (Knowledge Base section)
- Never access data outside user_id scope
- Log all actions in audit_trail
- If unsure about eligibility, run audit() tool
- Maintain tone: helpful, professional, LGPD-compliant

## SECURITY RULES
- User can only access their own data
- Never reveal data from other users
- If path traversal attempted, respond: "Cannot access that resource"
- All actions logged to json/memory/users/{user_id}/audit_trail.json
```

#### Testes (C10-C11, C13):
```bash
pytest tests/test_prompt_v4.py -v
pytest tests/test_memory_injection.py -v
```

#### Entregável:
- ✅ Prompt v4.0 funcional
- ✅ Memory injected corretamente
- ✅ Tools callable from LLM

---

### FASE 4: Isolamento & Segurança (Março 2027)
**Objetivo**: Hardening de segurança e conformidade LGPD

#### Arquivos a Atualizar:
```
src/health_refund_assistant/auth/
├── data_isolation.py         # Path validation, boundaries
├── rate_limiter.py           # (NOVO) Rate limiting por user
└── lgpd_compliance.py        # (NOVO) Direitos de dados

tests/
├── test_user_isolation.py    # (NOVO) C04-C05
├── test_lgpd_compliance.py   # (NOVO) C09, C14-C15
└── test_security.py          # (NOVO) C13
```

#### Implementação:
1. Path validation: Bloquear `../`, `~`, wildcard patterns
2. Rate limiting: Max 100 requests/hour/user
3. LGPD rights:
   - Right to access (C09)
   - Right to export
   - Right to delete
4. Error handling robusto

#### Testes (C04, C05, C09, C13-C15):
```bash
pytest tests/test_user_isolation.py -v
pytest tests/test_lgpd_compliance.py -v
pytest tests/test_security.py -v
```

#### Entregável:
- ✅ Todas as C04-C15 passando
- ✅ LGPD compliance report
- ✅ Security audit documentation

---

### FASE 5: Extension Alignment (Abril 2027)
**Objetivo**: Integrar com VS Code + Web (MCP Protocol)

#### Arquivos a Criar:
```
src/extensions/               # (NOVO)
├── copilot_mcp.py           # Copilot MCP server
├── handlers/
│   ├── pdf_handler.py
│   ├── user_handler.py
│   └── memory_handler.py
└── schemas/
    ├── user_request.json
    ├── audit_response.json
    └── memory_state.json

extension/
├── manifest.json             # (ATUALIZADO)
└── copilot_integration.js    # (NOVO)
```

#### Implementação:
1. MCP server rodando em background
2. VS Code extension comunica via JSON-RPC
3. Web UI integrada

#### Testes:
```bash
pytest tests/test_mcp_server.py -v
pytest tests/test_extension.py -v
```

#### Entregável:
- ✅ MCP server funcional
- ✅ VS Code extension updated
- ✅ Web UI integration complete

---

## 📊 Comparativo: Antes vs Depois

| Aspecto | Antes (v1.0) | Depois (v4.0) |
|--------|-------------|--------------|
| **Memória** | ❌ Sem memória | ✅ Por usuário |
| **Histórico** | ❌ Sem contexto | ✅ Últimas 5-10 msgs |
| **Validação** | ❌ Sem auth | ✅ PIN simples |
| **Isolamento** | ❌ Risco mistura | ✅ Total isolamento |
| **Tools** | ❌ Monolítico | ✅ Modular + registry |
| **Knowledge** | ❌ Hardcoded | ✅ Dinâmico (JSON) |
| **Auditoria** | ❌ Sem logs | ✅ Completo audit_trail |
| **LGPD** | ❌ Risco | ✅ Compliant |
| **Extension** | ❌ Básico | ✅ MCP integrado |

---

## 🎯 Marcos Importantes

```
Nov 2026: ✅ Entrega 02/12 (v1.0 atual)
           Reorganização + Documentação + Codespaces

Dez 2026: 🚀 FASE 1 - Core Foundation
           Knowledge + Memory + Auth básicos

Jan 2027: 🛠️ FASE 2 - Tools Registry
           5 tools implementados

Fev 2027: 💡 FASE 3 - Prompt v4.0
           Memory injection + Tools callable

Mar 2027: 🔒 FASE 4 - Security Hardening
           LGPD compliance + Isolamento total

Abr 2027: 🔌 FASE 5 - Extension Alignment
           MCP + VS Code + Web integração

Mai 2027: ✨ v2.0 Release
           AI Agent Project completo
```

---

## 🔄 Dependências Entre Fases

```
FASE 1 (Core)
  ├─ knowledge.py
  ├─ memory.py
  └─ auth/
       ↓
     FASE 2 (Tools)
       ├─ vlm_tool.py
       ├─ reconciliation_tool.py
       ├─ audit_tool.py
       └─ orchestrator.py
            ↓
          FASE 3 (Prompt v4.0)
            ├─ prompt injection
            └─ tool calling
                 ↓
               FASE 4 (Security)
                 ├─ data_isolation
                 ├─ rate_limiter
                 └─ lgpd_compliance
                      ↓
                    FASE 5 (Extension)
                      ├─ copilot_mcp.py
                      └─ web integration
```

---

## 📝 Documentação por Fase

| Fase | Documentação Principal | Links |
|------|------------------------|-------|
| 1 | AI_AGENT_ARCHITECTURE.md | Knowledge, Memory, Auth |
| 2 | CASOS_TESTE_MEMORY_ISOLATION.md | C01-C15 |
| 3 | docs/caderno_projeto.md (R2) | Prompt v4.0 engineering |
| 4 | SECURITY_LGPD_GUIDE.md | (NOVO) |
| 5 | EXTENSION_MCP_GUIDE.md | (NOVO) |

---

## ✅ Checklist Incremental

### FASE 1 ✓
- [ ] knowledge.py implementado
- [ ] memory.py implementado
- [ ] auth/ folder complete
- [ ] json/knowledge/ populated
- [ ] json/memory/ schema defined
- [ ] C01-C03, C06-C08 passing
- [ ] Docs atualizada

### FASE 2 ✓
- [ ] tools/ folder complete
- [ ] orchestrator.py implementado
- [ ] ToolRegistry funcional
- [ ] C10-C11 passing
- [ ] Docs atualizada

### FASE 3 ✓
- [ ] prompt v4.0 criado
- [ ] Memory injection funciona
- [ ] Tool calling funciona
- [ ] Assistant.py atualizado
- [ ] C10-C11 completo
- [ ] Docs atualizada

### FASE 4 ✓
- [ ] data_isolation hardened
- [ ] rate_limiter implementado
- [ ] lgpd_compliance implementado
- [ ] C04-C05, C09, C13-C15 passing
- [ ] Security audit completo
- [ ] Docs atualizada

### FASE 5 ✓
- [ ] copilot_mcp.py criado
- [ ] MCP server rodando
- [ ] Extension atualizada
- [ ] Web UI integrada
- [ ] Testes de integração passing
- [ ] Docs atualizada

---

## 🎓 Conceitos Fundacionais

Estudar/Implementar:
- [ ] Foundry concepts (Knowledge, Memory, Tools)
- [ ] User session management
- [ ] Multi-user concurrency
- [ ] MCP (Model Context Protocol)
- [ ] Prompt injection attacks & defenses
- [ ] LGPD compliance patterns
- [ ] AI agent design patterns
