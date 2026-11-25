# 00_INDICE_NAVEGACAO.md

## 🎯 Bem-vindo à Extensão Chrome: Care Plus Reembolsos Coletor

Escolha seu perfil de leitura:

---

## 👤 Novo Usuário? (5 minutos)

Você quer usar a extensão agora.

**Leia nesta ordem:**
1. [`README.md`](./README.md) — Visão geral (2 min)
2. [`50_docs/01_leia_primeiro.md`](./50_docs/01_leia_primeiro.md) — Conceitos (2 min)
3. [`50_docs/02_instalacao.md`](./50_docs/02_instalacao.md) — Instalar (1 min)
4. [`50_docs/03_uso_basico.md`](./50_docs/03_uso_basico.md) — Usar (1 min)

**Resultado:** Extensão instalada e primeira coleta feita ✅

---

## 🔍 Revisor? (1-2 horas)

Você quer entender tudo antes de usar.

**Leia nesta ordem:**
1. [`README.md`](./README.md) — Visão geral
2. [`50_docs/01_leia_primeiro.md`](./50_docs/01_leia_primeiro.md) — Conceitos
3. [`50_docs/02_instalacao.md`](./50_docs/02_instalacao.md) — Instalação
4. [`50_docs/03_uso_basico.md`](./50_docs/03_uso_basico.md) — Uso básico
5. [`50_docs/05_estrutura_json.md`](./50_docs/05_estrutura_json.md) — Formato dados
6. [`50_docs/06_manifest_mv3.md`](./50_docs/06_manifest_mv3.md) — Técnico (Chrome)
7. [`50_docs/07_troubleshooting.md`](./50_docs/07_troubleshooting.md) — Problemas

**Resultado:** Compreensão completa do projeto ✅

---

## 🛠️ Executor/Testador? (20 minutos)

Você vai usar a extensão em contexto produtivo.

**Leia nesta ordem:**
1. [`50_docs/02_instalacao.md`](./50_docs/02_instalacao.md) — Instalação completa
2. [`50_docs/03_uso_basico.md`](./50_docs/03_uso_basico.md) — Workflow normal
3. [`50_docs/04_lm_studio.md`](./50_docs/04_lm_studio.md) — Integração (se aplicável)
4. [`50_docs/07_troubleshooting.md`](./50_docs/07_troubleshooting.md) — Problemas (referência rápida)

**Resultado:** Pronto para coletas em produção ✅

---

## 🧠 Arquiteto? (1-2 horas)

Você quer entender design e contribuir.

**Leia nesta ordem:**
1. [`README.md`](./README.md) — Visão geral
2. [`50_docs/01_leia_primeiro.md`](./50_docs/01_leia_primeiro.md) — Conceitos
3. [`50_docs/06_manifest_mv3.md`](./50_docs/06_manifest_mv3.md) — Arquitetura Chrome MV3
4. [`50_docs/08_desenvolvimento.md`](./50_docs/08_desenvolvimento.md) — Como modificar
5. Código: `10_popup/`, `20_background/`, `30_content/`, `40_collector/`

**Resultado:** Capaz de estender/modificar ✅

---

## 🎤 Apresentador? (30 minutos)

Você vai explicar para executivos/stakeholders.

**Leia nesta ordem:**
1. [`README.md`](./README.md) — Visão geral (5 min)
2. [`50_docs/01_leia_primeiro.md`](./50_docs/01_leia_primeiro.md) — Conceitos (5 min)
3. [`50_docs/03_uso_basico.md`](./50_docs/03_uso_basico.md) — Demo workflow (5 min)
4. [`50_docs/05_estrutura_json.md`](./50_docs/05_estrutura_json.md) — Exemplo saída (5 min)
5. [`50_docs/07_troubleshooting.md`](./50_docs/07_troubleshooting.md) — Problemas reais (5 min)

**Resultado:** Preparado para apresentação ✅

---

## 📂 Estrutura de Arquivos

```
src/extension/
├── README.md                           ⭐ Comece aqui
├── 01_manifest.json                    Chrome MV3 config
│
├── 10_popup/                           Interface
│   ├── popup.html
│   └── popup.js
│
├── 20_background/                      Service Worker
│   └── background.js
│
├── 30_content/                         Content Script
│   └── bridge.js
│
├── 40_collector/                       Parser
│   └── collector.js
│
├── 50_docs/                            📚 Documentação Completa
│   ├── 01_leia_primeiro.md             Conceitos (ler se novo)
│   ├── 02_instalacao.md                Como instalar
│   ├── 03_uso_basico.md                Como usar
│   ├── 04_lm_studio.md                 Integração LM Studio
│   ├── 05_estrutura_json.md            Formato dos dados
│   ├── 06_manifest_mv3.md              Arquitetura técnica
│   ├── 07_troubleshooting.md           Problemas e soluções
│   └── 08_desenvolvimento.md           Como modificar
│
├── 60_schemas/                         Validação
│   └── export.schema.json              JSON schema
│
└── 70_assets/                          Recursos
    ├── icons/                          (Futuros ícones)
    └── styles/                         (Futuros CSS)
```

---

## 🔍 Busca Rápida

**Dúvida:** | **Documento:**
---|---
Como instalar? | [`02_instalacao.md`](./50_docs/02_instalacao.md)
Como usar? | [`03_uso_basico.md`](./50_docs/03_uso_basico.md)
Qual é a saída JSON? | [`05_estrutura_json.md`](./50_docs/05_estrutura_json.md)
Algo deu errado | [`07_troubleshooting.md`](./50_docs/07_troubleshooting.md)
Quero modificar código | [`08_desenvolvimento.md`](./50_docs/08_desenvolvimento.md)
LM Studio? | [`04_lm_studio.md`](./50_docs/04_lm_studio.md)
MV3/Chrome? | [`06_manifest_mv3.md`](./50_docs/06_manifest_mv3.md)
Conceitos gerais | [`01_leia_primeiro.md`](./50_docs/01_leia_primeiro.md)

---

## ⚡ Início Rápido (3 Passos)

```bash
1. Instale:   chrome://extensions → Load → src/extension/
2. Use:       Clique ícone → "Coletar Reembolsos"
3. Resultado: JSON em Downloads
```

Veja [`50_docs/02_instalacao.md`](./50_docs/02_instalacao.md) para detalhes.

---

## ✅ Checklist Pré-Uso

- [ ] Extension instalada em development mode
- [ ] Testei com 1 beneficiário (teste curto)
- [ ] JSON foi baixado sem erros
- [ ] Dados parecem completos
- [ ] Lieusemos [`07_troubleshooting.md`](./50_docs/07_troubleshooting.md) se houver dúvidas

---

## 🆘 Precisa de Ajuda?

| Situação | Vá para |
|----------|---------|
| Dúvida técnica | [`50_docs/06_manifest_mv3.md`](./50_docs/06_manifest_mv3.md) |
| Erro ao usar | [`50_docs/07_troubleshooting.md`](./50_docs/07_troubleshooting.md) |
| Quer modificar | [`50_docs/08_desenvolvimento.md`](./50_docs/08_desenvolvimento.md) |
| Conceitos | [`50_docs/01_leia_primeiro.md`](./50_docs/01_leia_primeiro.md) |

---

**Última atualização:** 2026-11-25  
**Versão:** 1.1.0  
**Status:** ✅ Pronto para uso
