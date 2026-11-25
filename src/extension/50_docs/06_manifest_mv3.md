# 6. Manifest MV3 – Referência Técnica

## O que é Manifest V3?

**Manifest V3** (MV3) é a arquitetura atual do Chrome para extensões (desde 2023).

Substituiu MV2 (deprecated) com melhorias:
- ✅ **Segurança:** Menos acesso privilegiado
- ✅ **Performance:** Service Workers em vez de background pages
- ✅ **Isolamento:** Menos risco de injeção

---

## Arquivo: `01_manifest.json`

```json
{
  "manifest_version": 3,
  "name": "Care Plus – Coletor de Reembolsos",
  "version": "1.1.0",
  "description": "Navega pela Consulta de Reembolsos da Care Plus, extrai...",
  
  "permissions": ["scripting", "storage", "downloads", "activeTab"],
  
  "host_permissions": [
    "https://*.careplus.com.br/*",
    "http://localhost/*",
    "http://127.0.0.1/*"
  ],
  
  "background": { "service_worker": "20_background/background.js" },
  
  "action": {
    "default_popup": "10_popup/popup.html",
    "default_title": "Coletar Reembolsos"
  },
  
  "content_scripts": [
    {
      "matches": ["https://*.careplus.com.br/portal/portal/modulos/reembolso/*"],
      "js": ["30_content/bridge.js"],
      "run_at": "document_idle"
    }
  ]
}
```

---

## Campos Explicados

### Metadados Básicos

| Campo | Valor | Significado |
|-------|-------|-------------|
| `manifest_version` | `3` | Versão do Chrome Extensions (obrigatório) |
| `name` | "Care Plus..." | Nome exibido na loja e em Extensions |
| `version` | "1.1.0" | Versão da extensão (incrementar ao atualizar) |
| `description` | "Navega..." | Descrição breve (mostrada em Extensions) |

### Permissões

```json
"permissions": ["scripting", "storage", "downloads", "activeTab"]
```

| Permissão | Função |
|-----------|--------|
| `scripting` | Permite injetar/executar `bridge.js` |
| `storage` | Acessa `chrome.storage.local` (guardar config) |
| `downloads` | Permite chamar `chrome.downloads.download()` |
| `activeTab` | Acesso à aba ativa do navegador |

### Host Permissions

```json
"host_permissions": [
  "https://*.careplus.com.br/*",
  "http://localhost/*",
  "http://127.0.0.1/*"
]
```

Permite acesso a:
- `https://*.careplus.com.br/*` — Domínios Care Plus (qualquer subdomínio)
- `http://localhost/*` — Servidor local (LM Studio, aplicação)
- `http://127.0.0.1/*` — Alias de localhost

---

## Background Service Worker

```json
"background": { "service_worker": "20_background/background.js" }
```

**O que faz:** Script que roda em segundo plano (mesmo com popup fechado).

**Uso na extensão:**
- Orquestra a coleta (coordena bridge + collector)
- Gerencia downloads
- Monitora eventos do Chrome

**Arquivo:** [`20_background/background.js`](../20_background/background.js)

---

## Ação (Popup)

```json
"action": {
  "default_popup": "10_popup/popup.html",
  "default_title": "Coletar Reembolsos"
}
```

| Campo | Significado |
|-------|-------------|
| `default_popup` | Arquivo HTML que abre ao clicar ícone |
| `default_title` | Tooltip ao passar mouse (Chrome, Edge, Brave) |

**Arquivo:** [`10_popup/popup.html`](../10_popup/popup.html)

---

## Content Scripts

```json
"content_scripts": [
  {
    "matches": ["https://*.careplus.com.br/portal/portal/modulos/reembolso/*"],
    "js": ["30_content/bridge.js"],
    "run_at": "document_idle"
  }
]
```

| Campo | Valor | Significado |
|-------|-------|-------------|
| `matches` | URL pattern | Quando injetar (aqui: páginas Care Plus reembolsos) |
| `js` | Array de scripts | Quais arquivos injetar (`bridge.js`) |
| `run_at` | `document_idle` | Quando injetar (após página carregada) |

**Arquivo:** [`30_content/bridge.js`](../30_content/bridge.js)

---

## Fluxo de Dados (MV3)

```
1. Usuário clica ícone
   ↓
2. Popup abre (10_popup/popup.html + popup.js)
   ↓
3. Usuário clica "Coletar Reembolsos"
   ↓
4. Background Service Worker acorda (20_background/background.js)
   ↓
5. Background navega/inicia coleta
   ↓
6. Content Script (30_content/bridge.js) injeta e executa
   ↓
7. Collector (40_collector/collector.js) lê dados
   ↓
8. Background recebe dados + baixa JSON
   ↓
9. Popup mostra progresso/sucesso
```

---

## Atualizar Versão

Quando fazer mudanças:

1. **Atualizar versão** em `01_manifest.json`:
   ```json
   "version": "1.2.0"  // foi 1.1.0
   ```

2. **Recarregar extensão** em Chrome Extensions:
   - Vá para `chrome://extensions`
   - Clique **Recarregar** (ou F5)

---

## Referências Oficiais

- **Chrome Manifest V3:** https://developer.chrome.com/docs/extensions/mv3/
- **Service Workers:** https://developer.chrome.com/docs/extensions/mv3/service_workers/
- **Content Scripts:** https://developer.chrome.com/docs/extensions/mv3/content_scripts/

---

## Próximo

- **Troubleshooting:** [`07_troubleshooting.md`](./07_troubleshooting.md)
- **Desenvolvimento:** [`08_desenvolvimento.md`](./08_desenvolvimento.md)
