# Plan Export Schema

Schema para dados de exportação do plano de saúde.

## Arquivo

### `plan_export.schema.json`
Contrato para registros de pedidos de reembolso exportados do sistema do plano.

**Propósito:** Define estrutura de dados importados do plano (uma fila de pedidos).

**Consumidores:**
- [assessment.py](../../../src/health_refund_assistant/plan/assessment.py) (validação de imports)
- [json/plan/imports/exportacao_plano.md](../imports/exportacao_plano.md)
- [json/tests/synthetic/exportacao_ficticia.md](../../tests/synthetic/exportacao_ficticia.md) (dados sintéticos)
- [reconciliation.py](../../../src/health_refund_assistant/plan/reconciliation.py) (match de registros)

**Referência de documentação:** [plan_export.schema.md](plan_export.schema.md)

---

## Integração com Código

### `payment_estimate.schema.json`

Contrato da saída da tarefa de IA para estimativa de processamento em dias úteis.
Consulte [payment_estimate.schema.md](./payment_estimate.schema.md); o código
confere os valores antes de usá-los.

```python
from health_refund_assistant.core.json_contracts import carregar_schema_json, validar_contrato_json

# Carregar schema
schema = carregar_schema_json("plan_export.schema.json")

# Validar dados importados
validar_contrato_json(dados_importados, "plan_export.schema.json", origem="exportacao.json")
```

## Fluxo de Importação

1. **Entrada:** exportação JSON do plano de saúde
2. **Validação:** `plan_export.schema.json` valida estrutura
3. **Armazenamento:** [json/plan/imports/](../imports) (ver `exportacao_plano.md`)
4. **Uso:** Reconciliação busca matches entre notas e pedidos do plano
