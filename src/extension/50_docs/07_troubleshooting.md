# 7. Troubleshooting – Problemas Comuns

## Instalação

### "Pasta não contém manifest.json"
**Problema:** Erro ao carregar extensão sem compactação.
**Causa:** Selecionou uma subpasta (ex: `50_docs/`) em vez da raiz.
**Solução:**
1. Volte um nível
2. Certifique-se de que `01_manifest.json` está visível
3. Selecione essa pasta

### "Erro: arquivo manifest.json inválido"
**Problema:** Chrome rejeita o manifest.
**Causa:** Arquivo corrompido, formatação JSON errada, ou encoding.
**Solução:**
1. Valide JSON: https://jsonlint.com/
2. Copie o arquivo original do repositório
3. Reinstale

### "Extensão desaparece após reiniciar Chrome"
**Problema:** Extensão carregada desaparece.
**Causa:** Pasta foi movida, deletada, ou disco removido.
**Solução:**
1. Pasta deve estar em local **permanente** (não Área de Trabalho/Temp)
2. Recarregue em `chrome://extensions`
3. Se não aparecer, reinstale

---

## Uso

### "Popup não abre / não aparece ícone"
**Problema:** Clica em nada ou ícone não aparece na barra.
**Causa:** Extensão não instalada ou desabilitada.
**Solução:**
1. Vá para `chrome://extensions`
2. Procure "Care Plus" na lista
3. Se não houver, reinstale ([`02_instalacao.md`](./02_instalacao.md))
4. Se houver mas está cinza, clique botão **Habilitar**
5. Fixe na barra (ícone pino ao lado do nome)

### "Clico 'Coletar Reembolsos' e nada acontece"
**Problema:** Popup fecha mas página não muda.
**Causa:** Falha na injeção ou página errada.
**Solução:**
1. Certifique-se de estar na página **Consultar Reembolsos** do portal
2. URL deve conter `/portal/modulos/reembolso/`
3. Clique novamente (pode demorar 5s na primeira vez)
4. Verifique console (F12 → Console)

### "Popup não fecha / fica preso"
**Problema:** Popup fica aberto mesmo após clicar.
**Causa:** Background worker sobrecarregado.
**Solução:**
1. Feche popup (clique fora ou ESC)
2. Recarregue extensão em `chrome://extensions` (F5)
3. Tente novamente

---

## Coleta de Dados

### "Coleta fica presa no mesmo beneficiário"
**Problema:** Aviso azul mostra mesmo nome por muito tempo.
**Causa:** Página lenta, timeout ou DOM não carrega.
**Solução:**
1. Verifique internet (página Care Plus está rápida?)
2. Recarregue página (F5) e tente novamente
3. Reduza número de beneficiários ou período
4. Veja logs em F12 → Application

### "Dados incompletos / campos vazios"
**Problema:** JSON tem muitos campos `null` ou vazios.
**Causa:** Página Care Plus mudou estrutura HTML, ou dados não estavam disponíveis.
**Solução:**
1. Verifique se sinistro abre manualmente no portal (pode estar limitado)
2. Tente novamente (às vezes é timeout)
3. Se persistir, relate ao time ([`08_desenvolvimento.md`](./08_desenvolvimento.md))

### "Arquivo JSON não baixa"
**Problema:** Coleta termina mas nada aparece em Downloads.
**Causa:** Chrome bloqueou download ou pasta de Downloads está protegida.
**Solução:**
1. Verifique permissões de download do Chrome:
   - `chrome://settings/privacy` → Avançadas → Downloads
2. Escolha pasta de Downloads acessível
3. Libere pop-ups/downloads para `careplus.com.br` se houver bloqueio

---

## LM Studio (Integração)

### "Enviou ao LM Studio mas não gerou arquivo"
**Problema:** Coleta normal funciona, mas `-lmstudio.json` não aparece.
**Causa:** Servidor não respondeu, URL errada, ou modelo ausente.
**Solução:**
1. Verifique se LM Studio está rodando: Vá a `http://localhost:1235` no Chrome
   - Se carregar página LM Studio → ✅ OK
   - Se erro de conexão → Inicie servidor
2. Verifique URL no popup (padrão: `http://localhost:1235`)
3. Verifique nome do modelo (deve estar carregado em LM Studio)
4. Veja logs em F12 → Application

### "LM Studio conecta mas demora muito"
**Problema:** Coleta leva 5+ minutos.
**Causa:** Modelo grande ou computador lento.
**Solução:**
1. Use modelo mais leve: `mistral-7b` em vez de `llama-70b`
2. Reduza número de reembolsos
3. Aumente RAM disponível (feche outros apps)
4. Desative se não precisar (desmarque checkbox)

### "Erro de CORS ao enviar"
**Problema:** Console mostra erro CORS/origem.
**Causa:** LM Studio não permite origem Chrome.
**Solução:**
1. LM Studio usa Service Worker da extensão (sem CORS)
2. Se erro persiste, verifique versão LM Studio
3. Tente: `http://127.0.0.1:1235` em vez de `localhost`

---

## Erros Técnicos (Console)

Abra F12 → Application → Service Worker. Veja erros comuns:

| Erro | Significado | Solução |
|------|-------------|---------|
| `Uncaught ReferenceError: ... is not defined` | Função faltando | Recarregue extensão |
| `Failed to fetch` | Conexão com portal falhou | Verifique internet/portal |
| `Timeout in collector` | Parser levou > tempo limite | Tente novamente, portal lento |
| `Invalid JSON response` | Portal retornou HTML em vez de dados | Portal pode estar em manutenção |

---

## Restaurar Estado Padrão

Se tudo falhar:

1. **Remova a extensão:**
   - `chrome://extensions` → Care Plus → **Remover**

2. **Limpe dados:**
   - `chrome://settings/privacy` → Limpar dados (Cache, Cookies)

3. **Reinstale:**
   - Veja [`02_instalacao.md`](./02_instalacao.md)

---

## Relatar Problema

Se nenhuma solução acima funciona:

1. Grave os passos exatos para reproduzir
2. Tire screenshot do erro
3. Abra console (F12) e copie mensagens de erro
4. Vá para [`08_desenvolvimento.md`](./08_desenvolvimento.md) para relatar

---

## Próximo

- **Desenvolvimento:** [`08_desenvolvimento.md`](./08_desenvolvimento.md)
- **Uso Básico:** [`03_uso_basico.md`](./03_uso_basico.md)
