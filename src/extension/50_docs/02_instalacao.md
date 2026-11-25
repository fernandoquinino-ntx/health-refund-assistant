# 2. Instalação – Passo a Passo

## Requisitos

- ✅ **Navegador:** Chrome, Edge, Brave, ou outro Chromium ≥ 93
- ✅ **Sistema:** Windows, macOS ou Linux
- ✅ **Acesso:** Portal Care Plus (`https://www.careplus.com.br`)

## Passo 1: Preparar a Pasta

### Opção A: Dos Fontes (Desenvolvedor)
Se você tem o repositório clonado:

```bash
# Pasta existe em:
src/extension/
```

### Opção B: Do ZIP (Usuário Final)
1. Baixe o arquivo da extensão (ou o repositório completo)
2. Descompacte em uma pasta local (ex: `C:\extensões\careplus` ou `~/extensões/careplus`)
3. Certifique-se de que o arquivo `01_manifest.json` está na raiz da pasta

---

## Passo 2: Abrir Chrome Extensions

1. Abra o Chrome/Chromium
2. Digite na barra de endereços:
   ```
   chrome://extensions
   ```
3. Pressione Enter

---

## Passo 3: Ativar Modo Desenvolvedor

No canto **superior direito** da página Extensions, você verá um botão/switch.

**Ativar: "Modo do Desenvolvedor"** (canto superior direito)

Depois aparecerá um novo botão: **"Carregar extensão sem compactação"**

---

## Passo 4: Selecionar Pasta

1. Clique em **"Carregar extensão sem compactação"**
2. Uma janela de seleção de pasta abrirá
3. Navegue até a pasta `src/extension/` (ou a pasta descompactada)
4. Selecione-a e clique **"Selecionar"** (ou equivalente no seu SO)

---

## Passo 5: Verificar Instalação

Volta para a página Extensions. Você verá:

```
Care Plus – Coletor de Reembolsos
Versão 1.1.0
Descrição: Navega pela Consulta de Reembolsos...

Botões:
  [Detalhes]  [Remover]  [Reparar]  [Desabilitar]
```

✅ **Se vê isso, está instalado!**

Próximo passo: Vá para a seção "Usar a Extensão" em [`03_uso_basico.md`](./03_uso_basico.md).

---

## Passo 6: Ancorá-la (Opcional)

Para facilitar acesso, **fixe a extensão** na barra de ferramentas:

1. Clique no ícone **Extensões** (quebra-cabeça) na barra de ferramentas
2. Localize "Care Plus – Coletor de Reembolsos"
3. Clique no **ícone de pino** para fixar
4. Agora aparecerá direto na barra (sem abrir o menu)

---

## Verificar Permissões

A extensão solicita permissões para:

| Permissão | Uso |
|-----------|-----|
| `scripting` | Injetar scripts na página Care Plus |
| `storage` | Guardar configurações (URL LM Studio, etc) |
| `downloads` | Baixar arquivo JSON em Downloads |
| `activeTab` | Acessar a aba ativa do navegador |

✅ Todas necessárias. Aceite ao instalar (ou manualmente na página de detalhes).

---

## Troubleshooting: Problemas Comuns

### "Pasta não contém manifest.json"
**Causa:** Você selecionou uma subpasta (ex: `src/extension/50_docs/`).
**Solução:** Volte um nível. Selecione a pasta que contém `01_manifest.json`.

### "Extensão desaparece após reiniciar Chrome"
**Causa:** Pasta foi movida ou deletada.
**Solução:** Recarregue (F5 na página Extensions) ou reinstale.

### "Erro: arquivo manifest.json inválido"
**Causa:** Arquivo corrompido ou formato errado.
**Solução:** Verifique se o arquivo é `01_manifest.json` (não `.txt` ou duplicado).

---

## Verificar Funcionamento

1. Abra a página de Extensions (`chrome://extensions`)
2. Clique em **Detalhes** da extensão
3. Vá para **Service Worker** (ou clique "Inspecionar vistas")
4. Console deve estar vazio (sem erros vermelhoes)

✅ Se não há erros vermelhos, está funcionando!

---

## Próximo: Usar a Extensão

Vá para [`03_uso_basico.md`](./03_uso_basico.md) para aprender a usar.

---

**Dúvidas?** Veja [`07_troubleshooting.md`](./07_troubleshooting.md).
