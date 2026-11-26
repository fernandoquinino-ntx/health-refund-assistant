# Care Plus – Coletor de Reembolsos

> **Reorganização não validada:** não carregue esta pasta no navegador. A versão
> carregável é [`extension/`](../../extension/); veja o
> [guia atual](../../docs/10_quickstart/03_comece_aqui_extension.md). As
> descrições abaixo precisam ser conferidas antes de substituir a extensão atual.

**Chrome Extension Manifest V3** para coletar automaticamente dados de sinistros/reembolsos do portal Care Plus e exportar em JSON.

## 🎯 Propósito

Acelera a coleta de dados de reembolsos do portal Care Plus, transformando um processo manual e demorado (clicar beneficiário por beneficiário) em uma exportação automatizada e estruturada.

## 📋 Visão Geral Rápida

| Aspecto | Descrição |
|--------|-----------|
| **Versão** | 1.1.0 |
| **Plataforma** | Chrome / Chromium (MV3) |
| **Função** | Coletar reembolsos de `https://*.careplus.com.br` |
| **Saída** | JSON estruturado (`careplus-reembolsos-AAAAMMDD-HHMM.json`) |
| **Integração** | Opcional: LM Studio para processamento adicional |

## 🚀 Início Rápido (3 Passos)

1. **Instalar:** [`50_docs/02_instalacao.md`](./50_docs/02_instalacao.md)
2. **Usar:** [`50_docs/03_uso_basico.md`](./50_docs/03_uso_basico.md)
3. **Explorar:** [`50_docs/05_estrutura_json.md`](./50_docs/05_estrutura_json.md)

## 📚 Documentação Completa

| Documento | Propósito |
|-----------|-----------|
| [`01_leia_primeiro.md`](./50_docs/01_leia_primeiro.md) | Visão geral e conceitos-chave |
| [`02_instalacao.md`](./50_docs/02_instalacao.md) | Passo a passo instalação Chrome |
| [`03_uso_basico.md`](./50_docs/03_uso_basico.md) | Como usar a extensão |
| [`04_lm_studio.md`](./50_docs/04_lm_studio.md) | Integração com LM Studio (opcional) |
| [`05_estrutura_json.md`](./50_docs/05_estrutura_json.md) | Formato dados exportados |
| [`06_manifest_mv3.md`](./50_docs/06_manifest_mv3.md) | Referência técnica Chrome MV3 |
| [`07_troubleshooting.md`](./50_docs/07_troubleshooting.md) | Erros comuns e soluções |
| [`08_desenvolvimento.md`](./50_docs/08_desenvolvimento.md) | Contribuir / modificar |

## 🏗️ Estrutura do Projeto

```
src/extension/
├── 01_manifest.json          Chrome MV3 config
├── README.md                 Este arquivo
│
├── 10_popup/                 Interface do usuário (popup)
│   ├── popup.html            Markup HTML
│   └── popup.js              Lógica de interação
│
├── 20_background/            Service Worker (fundo)
│   └── background.js         Orquestrador de fundo
│
├── 30_content/               Scripts de conteúdo
│   └── bridge.js             Injetor na página Care Plus
│
├── 40_collector/             Lógica de coleta
│   └── collector.js          Parser + navegação
│
├── 50_docs/                  Documentação completa
│   ├── 01_leia_primeiro.md
│   ├── 02_instalacao.md
│   ├── 03_uso_basico.md
│   ├── 04_lm_studio.md
│   ├── 05_estrutura_json.md
│   ├── 06_manifest_mv3.md
│   ├── 07_troubleshooting.md
│   └── 08_desenvolvimento.md
│
├── 60_schemas/               Validação JSON
│   └── export.schema.json    Schema dos dados exportados
│
└── 70_assets/                Recursos (ícones, estilos)
    ├── icons/
    │   ├── icon-16.png
    │   ├── icon-48.png
    │   ├── icon-128.png
    │   └── icon-256.png
    └── styles/
        └── common.css
```

## ✨ Destaques Técnicos

- **Manifest V3:** Arquitetura moderna do Chrome (Service Workers em vez de background pages)
- **Parsing Robusto:** Lida com DataTables, sub-itens expandíveis e paginação
- **Tolerância a Falhas:** Retry automático (1 tentativa) + logging detalhado
- **Flexibilidade de Período:** Detecta período da tela ou aceita entrada manual (com divisão em janelas)
- **Integração LM Studio:** Envia JSON para processamento local via API (zero CORS issues)
- **Formato Estruturado:** JSON com totalizações, campos brutos e metadados

## 🔗 Fluxo de Dados

```
Portal Care Plus
      ↓
   Bridge (30_content/bridge.js injetor)
      ↓
Collector (40_collector/collector.js parser)
      ↓
JSON Estruturado
      ↓
Export (Download) ou LM Studio (opcional)
```

## ⚙️ Requisitos

- Chrome/Chromium ≥ 93 (MV3 support)
- Acesso ao portal Care Plus (`https://*.careplus.com.br`)
- (Opcional) LM Studio running em `http://localhost:1235` (configurável)

## 🔐 Segurança

- ✅ Dados exportados salvam localmente (seus Downloads)
- ✅ Sem upload automático (apenas se você ativar LM Studio)
- ✅ Sem tracking ou dados pessoais enviados a terceiros
- ✅ Código aberto (veja [`08_desenvolvimento.md`](./50_docs/08_desenvolvimento.md))

## 📞 Suporte

Dúvidas ou problemas?
- Consulte [`07_troubleshooting.md`](./50_docs/07_troubleshooting.md)
- Abra uma issue no repositório
- Revise o console do Chrome (F12 → Application)

---

**Última atualização:** 2026-11-25  
**Versão:** 1.1.0  
**Mantido por:** Projeto health-refund-assistant
