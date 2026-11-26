# AI Agent Architecture - Health Refund Assistant

> **Proposta histórica:** descrições de autenticação, isolamento e ferramentas
> futuras não são funcionalidades implementadas. A aplicação possui memória
> local para um usuário, sem autenticação ou isolamento. Veja o
> [README atual](../../README.md).

> **Status**: Proposta de Alinhamento com Conceitos de Foundry/AI Agents  
> **Data**: 25 de novembro de 2026

---

## 📋 Visão Geral

Este documento propõe transformar o Health Refund Assistant em um **AI Agent Project completo**, alinhado com conceitos profissionais de:
- **KNOWLEDGE**: Base de conhecimento (exportação do plano, dados estatutários)
- **MEMORY**: Histórico de conversas por usuário
- **TOOLS**: Ferramentas/plugins disponíveis
- **USER IDENTITY**: Validação e isolamento de dados
- **EXTENSION**: Interface VS Code + Web

---

## 🏗️ Componentes da Arquitetura AI Agent

### 1. KNOWLEDGE BASE (Base de Conhecimento)
O que o agente **sabe** e usa para responder:

```
json/knowledge/
├── plan_exports/          # 📄 Exportação do plano (D-2)
│   ├── plano_saude_base.json
│   ├── reembolsos_historico.json
│   └── regras_cobertura.json
├── regulations/           # 📋 Regras e Leis
│   ├── plano_estatuto.json
│   ├── calendario_prazos.json
│   └── limites_cobertura.json
└── prompts/               # 🤖 Prompts Versionados
    ├── reembolso_assistente/v1.0-v4.0
    ├── vlm_extractor/v1.0-v4.0
    └── audit_rules/v1.0
```

**Implementação**:
```python
# src/health_refund_assistant/knowledge.py
class KnowledgeBase:
    def __init__(self, knowledge_path: str):
        self.plan_data = self.load_json("plan_exports/")
        self.rules = self.load_json("regulations/")
        self.prompts = self.load_prompts("prompts/")
    
    def get_plan_rules(self) -> dict:
        """Retorna regras do plano para validação"""
        return self.rules
    
    def get_prompt_version(self, name: str, version: str) -> str:
        """Carrega prompt versionado"""
        return self.prompts[name][version]
```

---

### 2. MEMORY SYSTEM (Histórico de Conversas)
Como o agente **lembra** de interações anteriores:

```
json/memory/
├── users/
│   ├── user_001_uuid/
│   │   ├── conversation_history.json
│   │   ├── submitted_cases.json
│   │   ├── audit_trail.json
│   │   └── preferences.json
│   ├── user_002_uuid/
│   └── ...
└── sessions/
    ├── session_uuid/
    │   └── messages.json
    └── ...
```

**Implementação**:
```python
# src/health_refund_assistant/memory.py
class UserMemory:
    def __init__(self, user_id: str, storage_path: str):
        self.user_id = user_id
        self.storage = storage_path
        self.conversations = self._load_conversations()
        self.submitted_cases = self._load_cases()
    
    def add_message(self, role: str, content: str, metadata: dict):
        """Adiciona mensagem ao histórico"""
        message = {
            "timestamp": datetime.now().isoformat(),
            "role": role,
            "content": content,
            "metadata": metadata
        }
        self.conversations.append(message)
        self._persist()
    
    def get_context_window(self, n: int = 5) -> list:
        """Retorna últimas N mensagens para contexto"""
        return self.conversations[-n:]
    
    def audit_log(self, action: str, details: dict):
        """Registra ação para auditoria LGPD"""
        pass
```

---

### 3. TOOLS (Ferramentas/Plugins)
Ações que o agente **pode fazer**:

```
src/health_refund_assistant/tools/
├── vlm_tool.py              # 👁️ Extração de PDFs (VLM)
├── reconciliation_tool.py   # ♻️ Reconciliação D-2
├── audit_tool.py            # ✅ Auditoria pré-envio
├── plan_lookup_tool.py      # 📄 Consulta base do plano
└── history_tool.py          # 📚 Consulta histórico do usuário
```

**Implementação**:
```python
# src/health_refund_assistant/tools/__init__.py
class ToolRegistry:
    tools = {
        "vlm_extract": VLMTool(),
        "reconcile": ReconciliationTool(),
        "audit": AuditTool(),
        "lookup_plan": PlanLookupTool(),
        "get_history": HistoryTool(),
    }
    
    @staticmethod
    def execute(tool_name: str, **kwargs):
        """Executa ferramenta registrada"""
        if tool_name not in ToolRegistry.tools:
            raise ValueError(f"Tool {tool_name} not found")
        return ToolRegistry.tools[tool_name].execute(**kwargs)
```

---

### 4. USER IDENTITY & VALIDATION (Isolamento de Dados)
Como **validar** o usuário e evitar vazamento de dados:

```
src/health_refund_assistant/auth/
├── user_validator.py        # Validação de identidade
├── access_control.py        # Controle de acesso
└── data_isolation.py        # Isolamento de dados por usuário
```

**Implementação**:
```python
# src/health_refund_assistant/auth/user_validator.py
class UserValidator:
    def __init__(self):
        self.valid_users = self._load_valid_users()
    
    def validate_user(self, user_id: str, pin: str) -> bool:
        """
        Valida usuário com PIN simples (4-6 dígitos)
        
        Fluxo:
        1. Usuário envia: "Olá, sou Fernando (123456)"
        2. Sistema valida PIN contra base
        3. Se válido: carrega memória do usuário
        4. Se inválido: mensagem segura "Não reconhecido"
        """
        user = self.valid_users.get(user_id)
        if not user:
            return False
        
        # Validação com hash (bcrypt)
        return self._verify_pin(pin, user["pin_hash"])
    
    def get_user_context(self, user_id: str) -> dict:
        """Retorna contexto isolado do usuário"""
        return {
            "user_id": user_id,
            "memory_path": f"json/memory/users/{user_id}/",
            "can_access_own_data_only": True
        }
```

---

### 5. PROMPTS & VERSIONS (Versionamento de Prompts)
Como os prompts **evoluem** e são **controlados**:

```
prompts/
├── reembolso_assistente/
│   ├── v1.0.md             # Initial version
│   ├── v2.0.md             # Added memory support
│   ├── v3.0.md             # Improved validation
│   └── v4.0.md             # Current - with memory + tools
├── vlm_extractor/
│   ├── v1.0.md
│   ├── v2.0.md
│   ├── v3.0.md
│   └── v4.0.md
└── audit_rules/
    └── v1.0.md
```

**Implementação em assistant.py**:
```python
# Usar memoria + tools + knowledge
prompt_v4 = """
# SYSTEM INSTRUCTIONS v4.0

## USER CONTEXT
Name: {user_name}
Session ID: {session_id}
Previous Interactions: {memory_count}

## AVAILABLE KNOWLEDGE
Plan Rules: {plan_rules_summary}
User History: {last_5_interactions}

## AVAILABLE TOOLS
1. vlm_extract: Extrair dados de PDF
2. reconcile: Reconciliar com base do plano
3. audit: Auditoria pré-envio
4. lookup_plan: Consultar plano
5. get_history: Histórico do usuário

## INSTRUCTIONS
- Sempre valide o usuário antes de acessar dados
- Use história para entender contexto
- Cite fontes (Knowledge Base)
- Registre ações em audit_trail
"""
```

---

### 6. EXTENSION ALIGNMENT
Integração com VS Code + Web:

```
extension/                    # 🔌 VS Code Extension
├── manifest.json
├── popup.js
├── collector.js              # Coleta dados (PDFs)
└── bridge.js                 # Bridge com Copilot

src/extensions/              # 🆕 NOVO: MCP/Protocol
├── copilot_mcp.py           # Copilot MCP server
├── handlers/
│   ├── pdf_handler.py
│   ├── user_handler.py
│   └── memory_handler.py
└── schemas/
    ├── user_request.json
    ├── audit_response.json
    └── memory_state.json
```

---

## 📊 Fluxo Completo com Memory + Tools

```
┌─────────────────┐
│   Usuário       │
│  "Olá, sou      │
│   Fernando      │
│   (123456)"     │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────┐
│  USER VALIDATOR                 │
│  - Valida PIN                   │
│  - Carrega User Context         │
│  - Acessa Memory                │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│  ORCHESTRATOR (assistant.py)    │
│  - Carrega última conversa      │
│  - Injeta Knowledge Base        │
│  - Monta prompt v4.0            │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│  LLM CALL                       │
│  - Usa memória como contexto    │
│  - Decisão: qual tool usar?    │
└────────┬────────────────────────┘
         │
    ┌────┴────┬──────────┬─────────┐
    │          │          │         │
    ▼          ▼          ▼         ▼
 VLM_TOOL  RECONCILE  AUDIT_TOOL  LOOKUP_PLAN
 Extract   D-2 Logic  Pre-send    History
    │          │          │         │
    └────┬─────┴──────┬───┴────┬────┘
         │            │        │
         ▼            ▼        ▼
    ┌────────────────────────────────┐
    │  MEMORY SYSTEM                 │
    │  - Salva conversa              │
    │  - Registra ações (audit_trail)│
    │  - Atualiza submitted_cases    │
    └────┬───────────────────────────┘
         │
         ▼
    ┌────────────────────────┐
    │  RESPONSE              │
    │  Fundamentada + Logs   │
    └────────────────────────┘
```

---

## 🔒 Isolamento de Dados (Segurança LGPD)

**Regra Central**: Um usuário NUNCA pode acessar dados de outro

```python
# src/health_refund_assistant/auth/data_isolation.py
class DataIsolation:
    @staticmethod
    def enforce_user_boundary(user_id: str, requested_data_path: str):
        """
        Garante que user_id só acessa dados seus
        
        VÁLIDO:
        - user_001 acessa json/memory/users/user_001/
        
        INVÁLIDO:
        - user_001 tenta acessar json/memory/users/user_002/
        - user_001 tenta acessar json/knowledge/ (público ok)
        """
        # Implementar no orchestrador
        pass
    
    @staticmethod
    def audit_access(user_id: str, resource: str, action: str):
        """Log LGPD de cada acesso"""
        pass
```

---

## 🧪 Casos de Teste para Isolamento

```python
# tests/test_user_isolation.py
def test_user_cannot_access_other_user_data():
    """C01: Usuário A não consegue acessar dados de Usuário B"""
    user_a = UserValidator.validate_user("fernando", "123456")
    user_b_data = Memory.load("json/memory/users/user_002/")
    
    with pytest.raises(AccessDenied):
        Memory.get_data_for_user(user_a, user_b_data)

def test_user_isolation_with_malicious_input():
    """C02: Tentativa de path traversal (../../../)"""
    user_a = "fernando"
    malicious_path = "json/memory/users/../../"
    
    with pytest.raises(ValidationError):
        Memory.load_safe(user_a, malicious_path)

def test_audit_trail_logs_all_access():
    """C03: Todos os acessos são logados"""
    user_a = "fernando"
    Memory.add_message(user_a, "test")
    
    audit = Memory.get_audit_trail(user_a)
    assert len(audit) > 0
    assert audit[-1]["action"] == "add_message"

def test_memory_persistence_across_sessions():
    """C04: Memória persiste entre sessões"""
    user_a = "fernando"
    Memory.add_message(user_a, "Session 1 message")
    
    # Simular novo acesso
    memory_v2 = UserMemory(user_a)
    messages = memory_v2.get_context_window(n=10)
    
    assert any("Session 1" in m["content"] for m in messages)
```

---

## 📂 Estrutura Arquivos Propostos

```
src/health_refund_assistant/
├── knowledge.py             # 🆕 KnowledgeBase class
├── memory.py                # 🆕 UserMemory + MemorySystem
├── auth/                    # 🆕 Pasta de autenticação
│   ├── user_validator.py
│   ├── access_control.py
│   └── data_isolation.py
├── tools/                   # 🆕 Pasta de ferramentas
│   ├── __init__.py
│   ├── base_tool.py
│   ├── vlm_tool.py
│   ├── reconciliation_tool.py
│   ├── audit_tool.py
│   ├── plan_lookup_tool.py
│   └── history_tool.py
├── extensions/              # 🆕 Pasta de extensões
│   ├── copilot_mcp.py
│   └── schemas/
├── assistant.py             # ✏️ Atualizado com memory + tools
├── orchestrator.py          # 🆕 Orquestrador central
└── ...

json/knowledge/              # 🆕 Base de conhecimento
├── plan_exports/
├── regulations/
└── prompts_metadata/

json/memory/                 # 🆕 Memória por usuário
├── users/
│   ├── fernando_uuid/
│   │   ├── conversation_history.json
│   │   ├── submitted_cases.json
│   │   ├── audit_trail.json
│   │   └── preferences.json
│   └── ...
└── sessions/
```

---

## 🎯 Próximas Fases

**Fase 1**: Implementar core (Knowledge, Memory, Auth)
- [ ] `src/health_refund_assistant/knowledge.py`
- [ ] `src/health_refund_assistant/memory.py`
- [ ] `src/health_refund_assistant/auth/`

**Fase 2**: Integrar Tools
- [ ] `src/health_refund_assistant/tools/`
- [ ] Atualizar `assistant.py` para usar tools

**Fase 3**: Extensões
- [ ] `src/extensions/copilot_mcp.py`
- [ ] Atualizar VS Code extension

**Fase 4**: Casos de Teste
- [ ] `tests/test_user_isolation.py`
- [ ] `tests/test_memory_persistence.py`
- [ ] `tests/test_knowledge_access.py`

---

## 📝 Referências

- Foundry Concepts: Knowledge, Memory, Tools
- LGPD Compliance: Data isolation, Audit trails
- AI Agent Standards: Prompt versioning, Tool registry
