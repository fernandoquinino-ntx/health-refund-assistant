# Extension & Arquitetura AI Agent

> **Proposta histórica:** as descrições de situação atual, caminhos e integração
> abaixo estão desatualizadas e não comprovam funcionalidades. A extensão
> carregável exporta JSON; o usuário o importa na interface. Consulte o
> [guia atual](../10_quickstart/03_comece_aqui_extension.md).

> **Propósito**: Alinhar extension (VS Code) com arquitetura AI Agent  
> **Data**: 25 de novembro de 2026

---

## 📌 Situação Atual

### Extension (Browser-based)
```
extension/
├── manifest.json             # Chrome/Firefox manifest
├── popup.html/js             # UI popup
├── background.js             # Service worker
├── collector.js              # Coleta dados (PDFs)
├── bridge.js                 # Comunicação
└── LEIAME.md
```

**Funcionalidade Atual**:
- ✅ Coleta PDFs de emails/sites
- ✅ Envia para backend
- ✅ Exibe respostas

**Limitações**:
- ❌ Sem persistência de memória
- ❌ Sem autenticação
- ❌ Sem histórico do usuário
- ❌ Sem isolamento de dados

---

### src/ (Python backend)
```
src/health_refund_assistant/
├── assistant.py              # Orquestrador
├── vlm_extractor.py          # VLM extração
├── reconciliation.py         # Lógica D-2
├── assessment.py             # Auditoria
├── web_app.py                # Streamlit UI
└── [SEM extension/MCP]       # 🔴 FALTA!
```

---

## 🎯 Visão Alinhada

### Com Fase 5 (Abril 2027)

```
EXTENSION (VS Code + Browser)
  ↓ JSON-RPC (MCP Protocol)
MCP SERVER (src/extensions/)
  ↓
ORCHESTRATOR + MEMORY + TOOLS
  ↓
KNOWLEDGE BASE + LLM API
```

---

## 📂 Estrutura Proposta

### Pasta: `src/extensions/` (NOVO)

```
src/extensions/
├── __init__.py
├── copilot_mcp.py            # MCP server principal
├── handlers/
│   ├── __init__.py
│   ├── auth_handler.py       # Login do usuário
│   ├── pdf_handler.py        # Recebe PDFs
│   ├── query_handler.py      # Consultas
│   └── memory_handler.py     # Histórico
├── schemas/
│   ├── user_request.json
│   ├── auth_response.json
│   ├── memory_state.json
│   └── audit_response.json
└── protocols/
    ├── json_rpc.py           # JSON-RPC 2.0
    └── mcp_protocol.py       # MCP specifics
```

### Atualizar: `extension/` (Browser)

```
extension/
├── manifest.json             # Atualizar versão
├── popup.html                # UI melhorada
├── popup.js                  # Lógica pop
├── mcp_client.js             # (NOVO) Cliente MCP
├── auth_manager.js           # (NOVO) Gerenciar login
├── memory_ui.js              # (NOVO) Mostrar histórico
├── styles/
│   └── popup.css             # (NOVO) Estilos melhorados
└── LEIAME.md                 # Docs atualizado
```

---

## 🔄 Fluxo Comunicação

### Hoje (v1.0)
```
Extension → HTTP POST → web_app.py (Streamlit)
  ↓
Processa
  ↓
Responde JSON
  ↓
Extension → Exibe
```

### Amanhã (v4.0 + MCP)
```
Extension (UI)
  ↓
  └─ mcp_client.js (JSON-RPC)
       ↓
     MCP Server (copilot_mcp.py)
       ├─ auth_handler    (valida user)
       ├─ memory_handler  (carrega histórico)
       ├─ pdf_handler     (processa PDF)
       └─ query_handler   (orquestra resposta)
            ↓
       orchestrator.py
            ├─ KnowledgeBase (plan data)
            ├─ ToolRegistry (vlm, reconcile, audit)
            ├─ MemorySystem (user history)
            └─ PromptInjection (v4.0 + context)
            ↓
       LLM API (OpenAI/local)
            ↓
       Response (fundamentado)
       ↓
     MCP Server retorna
       ↓
     Extension exibe + salva em memory
```

---

## 💻 Código Exemplo

### MCP Server (src/extensions/copilot_mcp.py)

```python
# src/extensions/copilot_mcp.py

from fastapi import FastAPI, WebSocket
from typing import Dict, Any
import json
import asyncio

app = FastAPI()

class MCPServer:
    def __init__(self):
        self.auth_handler = AuthHandler()
        self.memory_handler = MemoryHandler()
        self.pdf_handler = PDFHandler()
        self.query_handler = QueryHandler()
        self.user_sessions: Dict[str, Dict] = {}
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle JSON-RPC 2.0 request from Extension
        
        Request format:
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "auth_login",
            "params": {"user_id": "fernando", "pin": "123456"}
        }
        """
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")
        
        try:
            if method == "auth_login":
                result = await self.auth_handler.login(params)
            
            elif method == "auth_logout":
                result = await self.auth_handler.logout(params)
            
            elif method == "get_memory":
                # Carrega histórico do usuário
                user_id = self._get_authenticated_user(params)
                result = await self.memory_handler.get_context(user_id)
            
            elif method == "submit_invoice":
                # Upload + processamento
                user_id = self._get_authenticated_user(params)
                result = await self.pdf_handler.process(
                    user_id, 
                    params.get("pdf_base64")
                )
            
            elif method == "query":
                # Consulta com histórico
                user_id = self._get_authenticated_user(params)
                result = await self.query_handler.process(
                    user_id,
                    params.get("message"),
                    params.get("invoice_id")  # opcional
                )
            
            else:
                raise ValueError(f"Unknown method: {method}")
            
            # JSON-RPC 2.0 response
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": result
            }
        
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": str(e)
                }
            }
    
    def _get_authenticated_user(self, params: Dict) -> str:
        """Verifica se usuário está autenticado"""
        session_token = params.get("session_token")
        if session_token not in self.user_sessions:
            raise ValueError("Unauthorized")
        return self.user_sessions[session_token]["user_id"]

@app.websocket("/mcp")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    server = MCPServer()
    
    while True:
        data = await websocket.receive_text()
        request = json.loads(data)
        response = await server.handle_request(request)
        await websocket.send_text(json.dumps(response))
```

---

### Extension Client (extension/mcp_client.js)

```javascript
// extension/mcp_client.js

class MCPClient {
    constructor(serverUrl = "ws://localhost:8000/mcp") {
        this.serverUrl = serverUrl;
        this.ws = null;
        this.requestId = 0;
        this.pendingRequests = new Map();
    }
    
    async connect() {
        return new Promise((resolve, reject) => {
            this.ws = new WebSocket(this.serverUrl);
            
            this.ws.onopen = () => {
                console.log("MCP Connected");
                resolve();
            };
            
            this.ws.onmessage = (event) => {
                const response = JSON.parse(event.data);
                this._handleResponse(response);
            };
            
            this.ws.onerror = reject;
        });
    }
    
    async login(userId, pin) {
        """Autentica usuário"""
        return await this._call("auth_login", {
            user_id: userId,
            pin: pin
        });
    }
    
    async logout() {
        """Desconecta usuário"""
        return await this._call("auth_logout", {});
    }
    
    async getMemory() {
        """Carrega histórico do usuário"""
        return await this._call("get_memory", {
            session_token: this.sessionToken
        });
    }
    
    async submitInvoice(pdfBase64) {
        """Envia PDF para processamento"""
        return await this._call("submit_invoice", {
            session_token: this.sessionToken,
            pdf_base64: pdfBase64
        });
    }
    
    async query(message, invoiceId = null) {
        """Consulta com memória"""
        return await this._call("query", {
            session_token: this.sessionToken,
            message: message,
            invoice_id: invoiceId
        });
    }
    
    async _call(method, params) {
        """Envia JSON-RPC request"""
        const id = ++this.requestId;
        const request = {
            jsonrpc: "2.0",
            id: id,
            method: method,
            params: params
        };
        
        return new Promise((resolve, reject) => {
            this.pendingRequests.set(id, {resolve, reject});
            this.ws.send(JSON.stringify(request));
            
            // Timeout
            setTimeout(() => {
                if (this.pendingRequests.has(id)) {
                    this.pendingRequests.delete(id);
                    reject(new Error("Request timeout"));
                }
            }, 10000);
        });
    }
    
    _handleResponse(response) {
        const id = response.id;
        const pending = this.pendingRequests.get(id);
        
        if (!pending) return;
        this.pendingRequests.delete(id);
        
        if (response.error) {
            pending.reject(new Error(response.error.message));
        } else {
            pending.resolve(response.result);
        }
    }
}

// Uso na extension
const mcp = new MCPClient();
await mcp.connect();
await mcp.login("fernando", "123456");
const memory = await mcp.getMemory();
console.log("Histórico:", memory);
```

---

## 🔐 Fluxo de Autenticação

```
┌──────────────────┐
│   Extension      │
│   "Login"        │
│   user + PIN     │
└────────┬─────────┘
         │
         ▼
   MCP Server
   auth_handler.login()
         │
         ├─ Valida PIN vs bcrypt hash
         ├─ Carrega user preferences
         ├─ Carrega memory/users/{user_id}/
         ├─ Gera session_token (JWT)
         ├─ Registra login em audit_trail
         │
         ▼
   Response: {
     "status": "AUTORIZADO",
     "session_token": "eyJhbG...",
     "user_name": "Fernando",
     "memory_summary": {
       "previous_conversations": 3,
       "last_case": {
         "id": "C0001",
         "status": "PAGO_INTEGRAL"
       }
     }
   }
         │
         ▼
   Extension
   - Salva session_token em localStorage
   - Exibe histórico ao usuário
   - Pronto para submit_invoice()
```

---

## 📊 Schemas JSON-RPC

### Request: auth_login

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "auth_login",
  "params": {
    "user_id": "fernando",
    "pin": "123456"
  }
}
```

### Response: auth_login

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "status": "AUTORIZADO",
    "session_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user_name": "Fernando",
    "user_id": "fernando",
    "memory": {
      "total_conversations": 5,
      "submitted_cases": 3,
      "last_interaction": "2026-11-25T16:00:00Z"
    }
  }
}
```

### Request: query

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "query",
  "params": {
    "session_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "message": "Qual foi o status da minha última nota?",
    "invoice_id": null
  }
}
```

### Response: query

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "response": "Olá Fernando! Vejo que você consultou a nota C0001 há 1 hora e ela foi Pago Integralmente. Quer enviar uma nova nota?",
    "context_used": {
      "memory_messages": 2,
      "knowledge_sections": ["plan_rules", "statute"],
      "tools_called": ["get_history"]
    },
    "audit_logged": true
  }
}
```

---

## 🎯 Alinhamento com Fases

### Hoje (02/12/2026)
```
Extension (browser) ← HTTP → web_app.py (Streamlit)
Sem memory, sem auth, sem isolamento
```

### Fase 1-2 (Dez-Jan)
```
Implementar:
- src/extensions/copilot_mcp.py (básico)
- auth_handler.py
- memory_handler.py
- Extension cliente (mcp_client.js)
```

### Fase 5 (Abril 2027)
```
Integração completa:
- MCP Server produção-ready
- Extension full-featured
- Autenticação + Memory + Tools
- Documentação MCP
```

---

## 📝 Documentação Extension

Arquivos a criar:
- [ ] `docs/EXTENSION_GUIDE.md` - Como usar extension
- [ ] `docs/MCP_PROTOCOL.md` - Especificação JSON-RPC
- [ ] `docs/EXTENSION_DEVELOPMENT.md` - Dev guide

---

## ✅ Checklist

**Para 02/12/2026** (entrega atual):
- [x] Extension funciona (v1.0)
- [x] Envia PDFs
- [x] Recebe respostas

**Para Fase 1-5**:
- [ ] MCP Server implementado
- [ ] Auth integrado
- [ ] Memory funcional
- [ ] Tools callable
- [ ] Extension atualizada
- [ ] Docs MCP completa
