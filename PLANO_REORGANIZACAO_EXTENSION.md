# Plano de Reorganização: Chrome Extension

## Status Atual ❌
```
extension/
├── background.js              (serviço de fundo)
├── bridge.js                  (injetor de scripts)
├── collector.js               (coleta de dados)
├── popup.js                   (UI do popup)
├── popup.html                 (HTML do popup)
├── manifest.json              (configuração Chrome)
├── leiame.md                  (instrução)
├── manifest.md                (documentação do manifest)
└── exportacao_reembolsos.md   (documentação da exportação)
```

**Problemas:**
- ❌ Nenhuma categoria/subcategorias
- ❌ Arquivos markdown soltos sem snake_case
- ❌ Sem números ordinais para navegação
- ❌ Sem separação clara: fontes vs docs
- ❌ Sem versionamento (v1.0, v1.1, etc)
- ❌ Sem README.md descrevendo a extensão

---

## Proposta de Reorganização ✅

```
src/
└── extension/                       (Novo: Extensão Chrome MV3)
    ├── 01_manifest.json             (Chrome MV3 config)
    ├── README.md                    (Visão geral da extensão)
    │
    ├── 10_popup/                    (Interface do usuário)
    │   ├── popup.html               (Markup)
    │   ├── popup.js                 (Lógica)
    │   └── styles.css               (CSS - novo)
    │
    ├── 20_background/               (Serviço de fundo)
    │   ├── background.js            (Service Worker)
    │   └── config.js                (Configuração - novo)
    │
    ├── 30_content/                  (Scripts de conteúdo)
    │   └── bridge.js                (Injetor na página)
    │
    ├── 40_collector/                (Lógica de coleta)
    │   ├── collector.js             (Orquestrador)
    │   ├── parser.js                (Parsing de dados - novo)
    │   ├── validators.js            (Validação - novo)
    │   └── exporters.js             (Exportação JSON - novo)
    │
    ├── 50_docs/                     (Documentação)
    │   ├── 01_leia_primeiro.md      (Guia de início)
    │   ├── 02_instalacao.md         (Passo a passo)
    │   ├── 03_uso_basico.md         (Como usar)
    │   ├── 04_lm_studio.md          (Integração LM Studio)
    │   ├── 05_estrutura_json.md     (Formato dos dados)
    │   ├── 06_manifest_mv3.md       (Referência técnica)
    │   ├── 07_troubleshooting.md    (Resolução de problemas)
    │   └── 08_desenvolvimento.md    (Para contribuidores)
    │
    ├── 60_schemas/                  (Schemas JSON)
    │   ├── manifest.schema.json     (MV3 schema)
    │   └── export.schema.json       (Formato exportação)
    │
    └── 70_assets/                   (Recursos)
        ├── icons/                   (Ícones)
        │   ├── icon-16.png
        │   ├── icon-48.png
        │   ├── icon-128.png
        │   └── icon-256.png
        └── styles/                  (Estilos compartilhados)
            └── common.css
```

---

## Benefícios ✨

| Aspecto | Antes | Depois |
|--------|-------|--------|
| **Organização** | Flat (9 arquivos) | Hierárquica (7 categorias) |
| **Navegação** | Desordenada | Ordenada (números ordinais) |
| **Documentação** | 2 arquivos `.md` | 8 documentos categorizados |
| **Manutenção** | Difícil localizar | Fácil (by responsibility) |
| **Extensibilidade** | Baixa | Alta (organização modular) |
| **Versionamento** | Não está claro | Claro (v1.0, v1.1, etc) |

---

## Etapas de Implementação

### Fase 1: Estrutura (10 min)
```bash
mkdir -p src/extension/{10_popup,20_background,30_content,40_collector,50_docs,60_schemas,70_assets/icons}
```

### Fase 2: Mover Arquivos JS (5 min)
```bash
mv extension/popup.html src/extension/10_popup/
mv extension/popup.js src/extension/10_popup/
mv extension/background.js src/extension/20_background/
mv extension/bridge.js src/extension/30_content/
mv extension/collector.js src/extension/40_collector/
mv extension/manifest.json src/extension/01_manifest.json
```

### Fase 3: Criar Arquivos Novos (20 min)
- `src/extension/README.md` - Visão geral
- `src/extension/50_docs/01_leia_primeiro.md` - Guia início
- `src/extension/50_docs/02_instalacao.md` - Instalação
- `src/extension/50_docs/03_uso_basico.md` - Uso
- `src/extension/50_docs/04_lm_studio.md` - Integração
- `src/extension/50_docs/05_estrutura_json.md` - Formato JSON
- `src/extension/50_docs/06_manifest_mv3.md` - Técnico
- `src/extension/50_docs/07_troubleshooting.md` - Problemas
- `src/extension/50_docs/08_desenvolvimento.md` - Contribuição

### Fase 4: Atualizar `manifest.json` (5 min)
Ajustar caminhos relativos:
```json
{
  "background": { "service_worker": "20_background/background.js" },
  "content_scripts": [
    {
      "js": ["30_content/bridge.js"]
    }
  ]
}
```

### Fase 5: Atualizar Git (5 min)
```bash
git add src/extension/
git rm -r extension/
git commit -m "refactor: reorganizar Chrome extension para estrutura modular"
```

### Fase 6: Atualizar Documentação Principal (10 min)
- Atualizar `01_leia_primeiro.md` - referência para extension
- Atualizar `docs/50_architecture/` - incluir extension no diagrama

---

## Arquivos a Eliminar

Após migração:
```bash
rm -rf extension/        # Pasta antiga
```

---

## Checklist Pós-Migração

- [ ] Extensão carrega sem erros no Chrome
- [ ] Todos os caminhos em `manifest.json` funcionam
- [ ] Docs estão em snake_case + ordinais
- [ ] `README.md` explica propósito e uso
- [ ] Schemas JSON validam dados corretamente
- [ ] Git mostra estrutura nova sem lixo
- [ ] `.gitignore` protege dados sensíveis (`.env`, tokens)
- [ ] CI/CD (se houver) funciona sem quebras

---

## Tempo Estimado Total: ~55 minutos ⏱️

| Fase | Tempo |
|------|-------|
| Estrutura | 10 min |
| Mover JS | 5 min |
| Criar docs | 20 min |
| Atualizar manifest | 5 min |
| Git + Limpeza | 5 min |
| Docs principais | 10 min |
| **TOTAL** | **~55 min** |

---

## Próximos Passos (Futuro)

1. **CI/CD para extension:** Validar `manifest.json` em cada commit
2. **Testes de integração:** Simular coleta de dados do portal
3. **Versioning claro:** Tags git `extension-v1.1.0`, etc
4. **Store Chrome Web:** Preparar para publicação oficial
5. **Documentação de API:** Descrever funções exportadas
6. **Logger estruturado:** Rastrear operações (já em agents.md)

