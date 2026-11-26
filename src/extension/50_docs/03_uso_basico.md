# 3. Uso Básico – Como Usar

> Este guia descreve a implementação fonte em `src/extension/`.

## Resumo de 60 Segundos

1. ✅ Instale a extensão ([`02_instalacao.md`](./02_instalacao.md))
2. ✅ Vá para Care Plus: `https://www.careplus.com.br/portal/` e faça login
3. ✅ Clique no ícone da extensão (canto superior direito)
4. ✅ Clique **"Coletar Reembolsos"**
5. ✅ Preencha datas (ou deixe em branco)
6. ✅ Espere (~1-2 min por beneficiário)
7. ✅ Arquivo JSON aparece em **Downloads**

---

## Passo a Passo Completo

### 1. Login no Portal

```
1. Abra https://www.careplus.com.br/portal/
2. Faça login com suas credenciais
3. Pode estar em qualquer página (home, consultas, etc)
```

### 2. Abrir Popup da Extensão

Clique no **ícone Care Plus** na barra de ferramentas (canto superior direito).

Aparecerá uma janela pequena (popup) com:

```
Care Plus – Coletor de Reembolsos
┌─────────────────────────────────┐
│                                 │
│  🔄 Coletar Reembolsos          │
│                                 │
│  De: [__/__/____]               │
│  Até: [__/__/____]              │
│                                 │
│  ☑ Enviar ao LM Studio          │
│  URL: [________________]        │
│  Modelo: [________________]     │
│                                 │
│  Histórico:                     │
│  • 2026-11-25 - 5 reembolsos   │
│  • 2026-11-24 - 12 reembolsos  │
│                                 │
└─────────────────────────────────┘
```

### 3. Preencher Datas (Opcional)

- **De/Até vazios:** Usa período da tela do portal
- **Com datas:** Coleta para esse intervalo (períodos > 6 meses são divididos em janelas)

Formato: `DD/MM/AAAA` (ex: `15/11/2026`)

### 4. Clicar "Coletar Reembolsos"

```
Botão grande: 🔄 COLETAR REEMBOLSOS
```

Ao clicar:
- ✅ Popup se fecha
- ✅ Página se abre automaticamente em "Consultar Reembolsos"
- ✅ Aviso azul aparece no canto superior

---

## Monitorar Progresso

Enquanto coleta, **barra azul** no canto superior mostra:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100%
Coletando: João (2 de 3)
Sinistro 123456... ✅
Sinistro 234567... ⏳
```

Leia o status em tempo real.

---

## Resultado: Arquivo JSON

Quando terminar, um arquivo é **baixado automaticamente**:

```
careplus-reembolsos-20261125-2000.json
```

**Nome:** `careplus-reembolsos-AAAAMMDD-HHMM.json`

Pode visualizar com:
- 📝 Qualquer editor de texto (Notepad, VSCode, etc)
- 🔍 Leitor JSON (web ou app)
- 🐍 Python: `json.load(open(...))`
- 🐍 JavaScript: `JSON.parse(...)`

---

## Integração com LM Studio (Opcional)

Se quiser processar os dados com um modelo local:

1. **Instale LM Studio:** https://lmstudio.ai/
2. **Carregue um modelo** (ex: `Mistral 7B`)
3. **Inicie servidor:** LM Studio → Server (padrão: `http://localhost:1235`)
4. **Volte na extensão** e marque ☑ "Enviar ao LM Studio"
5. **Preencha:** URL (`http://localhost:1235`) e Nome do modelo
6. **Clique:** "Coletar Reembolsos"

A extensão enviará o JSON para processamento. Resultado em:
```
careplus-reembolsos-20261125-2000-lmstudio.json
```

Veja [`04_lm_studio.md`](./04_lm_studio.md) para detalhes.

---

## Comportamento Esperado

| O que vê | Significa |
|----------|-----------|
| Aviso azul no canto | Coleta em progresso (normal) |
| Página muda de aba | Navegação automática (esperado) |
| Console mostra eventos | Logging detalhado (vejo em F12) |
| Popup fecha automaticamente | Sistema ocupado (voltará em 5s) |
| Arquivo em Downloads | ✅ Sucesso! |

---

## Leitura Pós-Coleta

Depois que terminar:

1. **Verifique o JSON:**
   ```bash
   python -m json.tool careplus-reembolsos-20261125-2000.json | less
   ```

2. **Importe na aplicação:**
   - Copie o arquivo para `json/plan/imports/`
   - Use a UI da aplicação para processar

3. **Estude a estrutura:**
   - Veja [`05_estrutura_json.md`](./05_estrutura_json.md)

---

## Erros Comuns

| Erro | Solução |
|------|---------|
| "Popup não abre" | Instale extensão ([`02_instalacao.md`](./02_instalacao.md)) |
| "Coleta fica presa" | Recarregue página (F5) e tente novamente |
| "Arquivo não baixa" | Verifique se Downloads está liberado no Chrome |
| "Dados incompletos" | Verifique datas e conexão; tente novamente |

Mais em [`07_troubleshooting.md`](./07_troubleshooting.md).

---

**Próximo:** Entenda a estrutura dos dados em [`05_estrutura_json.md`](./05_estrutura_json.md).
