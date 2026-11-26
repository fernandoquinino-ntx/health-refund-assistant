# 8. Desenvolvimento – Contribuir / Modificar

> Este guia descreve a implementação fonte única da extensão. Consulte o
> [guia atual](../../../docs/10_quickstart/03_comece_aqui_extension.md).

## Arquitetura Geral

```
30_content/bridge.js          Injeta script na página Care Plus
         ↓ (window.collectorAPI)
40_collector/collector.js     Parser + navegação (roda na página)
         ↓ (mensagens)
20_background/background.js   Orquestrador + downloads (service worker)
         ↓
10_popup/popup.js             UI + status (interface usuário)
```

**Fluxo:**
1. Usuário clica "Coletar" (popup)
2. Background inicia e chama bridge
3. Bridge injeta collector na página
4. Collector navega e faz parse
5. Dados retornam para background
6. Background baixa JSON e notifica popup

---

## Arquivos

### 1. `10_popup/popup.html`
Markup HTML do popup. Contém:
- Botão "Coletar Reembolsos"
- Inputs de datas (opcional)
- Checkbox LM Studio
- Histórico de coletas

**Modificar se:** Quiser adicionar campos/controles na UI.

### 2. `10_popup/popup.js`
Lógica do popup. Responsável por:
- Detectar cliques no botão
- Enviar mensagem ao background
- Receber atualizações de progresso
- Exibir histórico

**Modificar se:** Adicionar validação, novo campo, histórico persistente.

### 3. `20_background/background.js`
Service Worker principal. Responsável por:
- Escutar mensagens do popup
- Injetar content script
- Orquestrar coleta
- Fazer download JSON
- Integração LM Studio

**Modificar se:** Mudar lógica de coordenação, formato de saída, ou integração.

### 4. `30_content/bridge.js`
Injeta script na página Care Plus. Responsável por:
- Detectar `collector.js` injetado
- Executar `collector` na página
- Retornar dados ao background

**Modificar se:** Mudar injeção, adicionar validação DOM.

### 5. `40_collector/collector.js`
Parser de dados. Responsável por:
- Ler lista de beneficiários
- Navegar tabela `#tblAut1` (paginação)
- Expandir sub-itens (passo2/passo3)
- Parsear HTML → JSON estruturado
- Aplicar timeouts e retry

**Modificar se:** Portal mudou estrutura HTML, ou quer mudar lógica de parse.

### 6. `manifest.json`
Metadados Chrome MV3. Veja [`06_manifest_mv3.md`](./06_manifest_mv3.md).

---

## Começar a Modificar

### 1. Clonar/Baixar

```bash
# Se não tem ainda
git clone https://github.com/fernandoquinino-ntx/health-refund-assistant.git
cd health-refund-assistant
```

### 2. Carregue a versão atual em Modo Desenvolvimento

```
chrome://extensions → Habilitar "Modo Desenvolvedor"
→ "Carregar extensão sem compactação"
→ Selecione src/extension/
```

### 3. Edite arquivo

Edite os arquivos diretamente em `src/extension/`. Execute
`bash src/treinamento_visual/scripts/build_extension.sh` para gerar
`build/extension/` para testes ou empacotamento.

### 4. Recarregue

Em `chrome://extensions`, clique **Recarregar** (ou F5) na extensão.

Mudanças são aplicadas imediatamente.

### 5. Debug com Console

Abra DevTools (F12) na página:
- **Console:** Erros e logs
- **Network:** Requisições HTTP
- **Application → Service Worker:** Logs do background

---

## Exemplos de Modificações Comuns

### Mudar Campo Extraído

Supondo que quer adicionar "Código Procedimento" ao JSON.

1. Abra `40_collector/collector.js`
2. Procure função `parseDadosPasso3()`
3. Adicione:
   ```javascript
   const codigoProcedimento = element.querySelector('[data-field="codigo"]')?.textContent;
   ```
4. Inclua no objeto retornado:
   ```javascript
   return {
     // ... outros campos
     codigoProcedimento: codigoProcedimento,
   };
   ```
5. Recarregue extensão (F5 em `chrome://extensions`)
6. Coleta normal deve incluir novo campo

### Adicionar Validação

Supondo que quer validar se `valorFinalReembolsado > 0`.

1. Abra `40_collector/collector.js`
2. Adicione função:
   ```javascript
   function validarReembolso(reembolso) {
     if (reembolso.valorFinalReembolsadoNum <= 0) {
       console.warn("Reembolso com valor 0:", reembolso.numeroSinistro);
       return false;
     }
     return true;
   }
   ```
3. Chame antes de adicionar ao array:
   ```javascript
   if (validarReembolso(reembolso)) {
     reembolsos.push(reembolso);
   }
   ```
4. Recarregue

### Mudar Timeout

Supondo que coleta está muito lenta, quer aumentar timeout.

1. Abra `40_collector/collector.js`
2. Procure `const TIMEOUT = 3000;` (ou similar)
3. Mude para `const TIMEOUT = 5000;` (5 segundos)
4. Recarregue

---

## Testar

### Unit Tests (Se houver)

```bash
npm test
# ou
pytest tests/
```

### Teste Manual

1. Carregue extensão em development mode
2. Vá para portal Care Plus
3. Clique "Coletar Reembolsos"
4. Abra DevTools (F12) → Console
5. Verifique se há erros
6. Verifique JSON baixado

### Teste de Regressão

Colete dados conhecidos:
- Teste com 1 beneficiário
- Teste com período curto (1 mês)
- Verifique estrutura JSON
- Valide com schema (`60_schemas/export.schema.json`)

---

## Submeter Mudanças

Se quer contribuir com melhorias:

1. **Fork** do repositório
2. **Crie branch:** `git checkout -b feature/sua-melhoria`
3. **Faça mudanças** e teste localmente
4. **Commit:** `git commit -m "feat: descrição"`
5. **Push:** `git push origin feature/sua-melhoria`
6. **Pull Request** no repositório principal

---

## Referências de Código

### Funções Principais

| Função | Arquivo | Faz |
|--------|---------|-----|
| `iniciarColeta()` | `popup.js` | Inicia workflow |
| `orquestraColeta()` | `background.js` | Coordena coleta |
| `injetarCollector()` | `bridge.js` | Injeta script |
| `coletar()` | `collector.js` | Faz parse principal |
| `parseDadosPasso3()` | `collector.js` | Extrai um sinistro |

### Mensagens (Between Scripts)

```javascript
// popup → background
chrome.runtime.sendMessage({
  action: "iniciarColeta",
  datas: { de: "...", ate: "..." }
});

// background → popup (progresso)
chrome.runtime.sendMessage({
  action: "atualizarProgresso",
  progresso: "Coletando João..."
});

// background → LM Studio (opcional)
fetch('http://localhost:1235/v1/chat/completions', {
  method: 'POST',
  body: JSON.stringify({...})
});
```

---

## Logging

Para debugar, adicione logs:

```javascript
console.log("Debug info:", variavel);
console.warn("Aviso:", erro);
console.error("Erro crítico:", erro);
```

Veja em:
- **F12 → Console** (popup/página)
- **`chrome://extensions` → Service Worker → Inspecionar** (background)

---

## Próximo

- **Troubleshooting:** [`07_troubleshooting.md`](./07_troubleshooting.md)
- **Uso Básico:** [`03_uso_basico.md`](./03_uso_basico.md)
- **Repositório:** https://github.com/fernandoquinino-ntx/health-refund-assistant
