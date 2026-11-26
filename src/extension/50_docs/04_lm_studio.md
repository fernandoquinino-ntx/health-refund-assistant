# 4. LM Studio – Integração Opcional

> Este guia descreve a reorganização não validada em `src/extension/`. Consulte
> o [guia da extensão carregável](../../../extension/LEIAME.md).

## O que é LM Studio?

[LM Studio](https://lmstudio.ai/) é uma aplicação que roda **modelos de linguagem localmente** (Mistral, Llama, etc) sem enviar dados pela internet.

**Por que usar com Care Plus Extractor?**
- 🔐 **Privacidade:** Seus dados de reembolsos não saem do seu computador
- ⚡ **Rápido:** Processamento local (sem depender de APIs pagas)
- 🤖 **Flexível:** Escolha qualquer modelo aberto

---

## Requisitos

1. **LM Studio instalado:** https://lmstudio.ai/
2. **Um modelo carregado** (ex: `Mistral 7B`, `Llama 2`, etc)
3. **Servidor LM Studio rodando** (porta padrão: `1235`)
4. **~4-8 GB de RAM** (depende do modelo)

---

## Passo a Passo

### 1. Instalar LM Studio

Baixe em https://lmstudio.ai/ e instale (Windows, macOS, Linux).

### 2. Carregar um Modelo

1. Abra LM Studio
2. Menu "Discover" → Procure por um modelo (ex: `Mistral 7B`, `Neural 7B`)
3. Clique **Download** (primeira vez pode levar 5-30 min)

```
Modelos recomendados:
• mistral-7b (rápido, bom custo-benefício)
• neural-chat-7b (otimizado para chat)
• llama-2-7b (versátil)
```

### 3. Iniciar Servidor

1. No LM Studio, vá para **Local Server**
2. Selecione o modelo que baixou
3. Clique **▶ Start Server**

Esperado:
```
Local Server is running at http://localhost:1235
```

Deixe rodando (pode minimizar).

### 4. Habilitar na Extensão

Volte para o **popup da extensão** (Chrome):

```
☑ Enviar ao LM Studio

URL: http://localhost:1235
Modelo: mistral-7b
```

Preencha:
- **URL:** `http://localhost:1235` (padrão, mude se necessário)
- **Modelo:** Nome exato do modelo (ex: `mistral-7b-instruct-v0.1-gguf`)

### 5. Coletar Reembolsos

Clique **"Coletar Reembolsos"** (ver [`03_uso_basico.md`](./03_uso_basico.md)).

A extensão enviará os dados para processamento pelo modelo.

---

## Resultado

Dois arquivos serão baixados:

```
careplus-reembolsos-20261125-2000.json          (dados brutos)
careplus-reembolsos-20261125-2000-lmstudio.json (processado)
```

Formato `-lmstudio.json`:
```json
{
  "coleta_realizada_em": "2026-11-25T20:00:00",
  "dados_originais": { ...arquivo original... },
  "processamento_lm": {
    "modelo": "mistral-7b",
    "resumo": "5 reembolsos coletados, 3 pagos, 2 parciais",
    "insights": ["...", "..."],
    "detalhes_processados": [...]
  },
  "timestamp_processamento": "2026-11-25T20:05:00"
}
```

---

## Dúvidas Técnicas

### "Meu servidor LM Studio não está em http://localhost:1235"

No LM Studio, veja a URL exata no Local Server:
```
Pode estar em: http://127.0.0.1:1235
              http://192.168.1.100:1235
              Outra custom
```

Copie e cole no popup da extensão.

### "Qual é o nome exato do modelo?"

No LM Studio, selecione o modelo e copie o nome do seletor.
Pode incluir versão (ex: `mistral-7b-instruct-v0.1-gguf`).

### "Enviou mas não gerou -lmstudio.json"

Verifique:
1. Console do Chrome (F12 → Application)
2. Logs do LM Studio (console dele)
3. Tente com URL/modelo diferentes
4. Mais em [`07_troubleshooting.md`](./07_troubleshooting.md)

### "Qual modelo usar?"

**Iniciante:** `mistral-7b` (rápido, preciso)
**Intermediário:** `neural-chat-7b` (otimizado para chat)
**Avançado:** Teste o que quiser (Llama, Openchat, etc)

---

## Desabilitar LM Studio

Se não quiser mais:

1. Abra popup da extensão
2. Desmarque ☑ "Enviar ao LM Studio"
3. Clique "Coletar Reembolsos" normalmente (sem processamento adicional)

---

## Próximo

- **Estrutura JSON:** [`05_estrutura_json.md`](./05_estrutura_json.md)
- **Troubleshooting:** [`07_troubleshooting.md`](./07_troubleshooting.md)
- **Desenvolvimento:** [`08_desenvolvimento.md`](./08_desenvolvimento.md)
