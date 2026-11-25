# 🚀 COMECE AQUI – Chrome Extension Reorganizada

## ⚡ 3 Passos Rápidos

### 1️⃣ Leia o Mapa de Navegação
```bash
cd src/extension/
cat 00_indice_navegacao.md
```

### 2️⃣ Escolha Seu Perfil
- **Novo Usuário?** (5 min) → Comece em `50_docs/01_leia_primeiro.md`
- **Revisor?** (1-2h) → Comece em `50_docs/01_leia_primeiro.md` + complete
- **Executor?** (20 min) → Comece em `50_docs/02_instalacao.md`
- **Arquiteto?** (1-2h) → Comece em `50_docs/08_desenvolvimento.md`
- **Apresentador?** (30 min) → Comece em `README.md`

### 3️⃣ Teste a Extensão
```bash
# Chrome
chrome://extensions → "Load unpacked" → src/extension/
```

---

## 📂 Estrutura Rápida

| Pasta | O que é | Para quem? |
|-------|---------|-----------|
| [`50_docs/`](./src/extension/50_docs/) | 8 guias completos | Todos |
| [`10_popup/`](./src/extension/10_popup/) | Interface | Dev |
| [`20_background/`](./src/extension/20_background/) | Orquestrador | Dev |
| [`30_content/`](./src/extension/30_content/) | Injeta scripts | Dev |
| [`40_collector/`](./src/extension/40_collector/) | Parser de dados | Dev |
| [`60_schemas/`](./src/extension/60_schemas/) | JSON schema | Dev/Revisor |

---

## 📚 Documentos Principais

- **[`00_indice_navegacao.md`](./src/extension/00_indice_navegacao.md)** ⭐ Comece aqui
- **[`README.md`](./src/extension/README.md)** – Visão geral
- **[`50_docs/01_leia_primeiro.md`](./src/extension/50_docs/01_leia_primeiro.md)** – Conceitos
- **[`50_docs/02_instalacao.md`](./src/extension/50_docs/02_instalacao.md)** – Instalar
- **[`50_docs/07_troubleshooting.md`](./src/extension/50_docs/07_troubleshooting.md)** – Problemas
- **[`50_docs/08_desenvolvimento.md`](./src/extension/50_docs/08_desenvolvimento.md)** – Modificar

---

## 🎯 Próximas Ações

**Imediato:**
```bash
cd src/extension
cat 00_indice_navegacao.md        # Escolha seu perfil
```

**Curto prazo:**
1. Teste em Chrome: `chrome://extensions`
2. Coleta de dados: Clique "Coletar Reembolsos"
3. Verifique JSON em Downloads

**Médio prazo:**
- Se `extension/` antiga ainda existe → deletar
- Atualizar referências em `README.md` raiz

---

## ✅ Checklist

- [ ] Li `00_indice_navegacao.md`
- [ ] Identifiquei meu perfil
- [ ] Comecei leitura no documento recomendado
- [ ] Testei a extensão
- [ ] Funciona sem erros

---

**Status:** ✅ **PRONTO PARA USO**

**Comece:** [`src/extension/00_indice_navegacao.md`](./src/extension/00_indice_navegacao.md)
