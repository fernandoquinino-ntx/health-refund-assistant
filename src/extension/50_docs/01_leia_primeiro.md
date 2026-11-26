# 1. Leia Primeiro – Conceitos Essenciais

> **Reorganização não validada:** para instalar e usar a versão carregável,
> consulte o [guia atual](../../../docs/10_quickstart/03_comece_aqui_extension.md).

## O que é esta extensão?

**Care Plus Reembolsos Coletor** é uma extensão Chrome que automatiza a coleta de dados do portal de reembolsos da Care Plus.

Sem a extensão, você precisaria:
1. ✍️ Fazer login no portal Care Plus
2. 🔄 Clicar em cada beneficiário da sua conta
3. 📋 Para cada pessoa, consultar reembolsos mês a mês
4. 🖱️ Clicar em cada sinistro para ver detalhes
5. 📝 Copiar/colar manualmente ou usar DevTools

**Com a extensão:**
1. ✅ Login uma vez
2. ✅ Clique em "Coletar Reembolsos"
3. ✅ Espere (~1-2 min por beneficiário)
4. ✅ Arquivo JSON pronto em Downloads

---

## Fluxo Alto-Nível

```
1. BROWSER                    2. EXTENSÃO               3. SAÍDA
┌─────────────────┐          ┌──────────────┐          ┌─────────┐
│ Portal Care     │  Injeta  │ 30_content/  │          │ JSON    │
│ Plus            │ ────────→ │ bridge.js    │          │ File    │
│ *.careplus.     │          │              │          │ (Dwnld) │
│  com.br         │          └──────────────┘          └─────────┘
└─────────────────┘                 ↓
                          ┌──────────────────┐
                          │ 40_collector/    │
                          │ collector.js     │
                          │ (Parse + Nav)    │
                          └──────────────────┘
                                  ↓
                          ┌──────────────────┐
                          │ 20_background/   │
                          │ background.js    │
                          │ (Orquestra)      │
                          └──────────────────┘
                                  ↓
                          ┌──────────────────┐
                          │ 10_popup/        │
                          │ (UI + Progress)  │
                          └──────────────────┘
```

---

## Conceitos-Chave

### 1. **Beneficiários**
Pessoas vinculadas à sua conta Care Plus. A extensão coleta dados **por beneficiário**, um por vez.

```
Sua Conta Care Plus
├── Você
├── Cônjuge
├── Filho 1
├── Filho 2
└── Dependente
```

Cada um tem seu histórico de reembolsos separado.

### 2. **Sinistros e Reembolsos**
- **Sinistro:** Evento de saúde (consulta, exame, internação) com número único
- **Reembolso:** Solicitação de reembolso associada ao sinistro
- **Status:** Pago, parcialmente pago, recusado, em análise, etc.

Exemplo:
```
Sinistro #123456
├── Beneficiário: João Silva
├── Procedimento: Consulta Cardiologia
├── Data: 2026-11-20
├── Valor Solicitado: R$ 500
├── Valor Reembolsado: R$ 350 (coparticipação: R$ 150)
└── Status: PAGO ✅
```

### 3. **Período**
A extensão coleta reembolsos dentro de um **período de datas** (ex: 01/11/2026 a 30/11/2026).

- Se deixar **em branco**, usa datas da tela do portal (padrão)
- Se preencher **De/Até**, divide períodos longos em janelas de 6 meses
- Remove duplicatas automaticamente

### 4. **Sub-itens**
Alguns sinistros têm sub-itens (ex: internação com múltiplas diárias). A extensão:
- Detecta e expande sub-itens
- Lê detalhes de cada um
- Inclui tudo no JSON final

---

## Dados de Saída

A extensão salva um arquivo JSON com esta estrutura:

```json
{
  "coleta_realizada_em": "2026-11-25T20:00:00",
  "total": 5,
  "totalPorPessoa": {"João": 2, "Maria": 3},
  "pessoas": ["João", "Maria"],
  "reembolsos": [
    {
      "pessoaConsultada": "João",
      "numeroSinistro": "123456",
      "beneficiario": "João",
      "status": "PAGO",
      "valorSolicitado": 500.00,
      "valorCoparticipacao": 150.00,
      "valorFinalReembolsado": 350.00,
      "descricao": "Consulta Cardiologia",
      ...
    }
  ],
  "erros": []
}
```

✅ **Uso:** Importe este JSON na aplicação health-refund-assistant para análise, rastreamento ou integração com seu sistema.

---

## Próximos Passos

1. **Instalar:** Veja [`02_instalacao.md`](./02_instalacao.md)
2. **Usar:** Veja [`03_uso_basico.md`](./03_uso_basico.md)
3. **Entender Dados:** Veja [`05_estrutura_json.md`](./05_estrutura_json.md)
4. **Integração LM Studio:** Veja [`04_lm_studio.md`](./04_lm_studio.md) (opcional)

---

**Pronto para começar?** → Próximo: [`02_instalacao.md`](./02_instalacao.md)
