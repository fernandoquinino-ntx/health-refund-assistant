# Plan Export Schema

Schema para dados de exportação do plano de saúde.

## Arquivo

### `plan_export.schema.json`
Contrato para registros de pedidos de reembolso exportados do sistema do plano.

**Propósito:** Define estrutura de dados importados do plano (uma fila de pedidos).

**Consumidores:**
- [assessment.py](/src/health_refund_assistant/assessment.py) (validação de imports)
- [json/plan/imports/exportacao_plano.md](/json/plan/imports/exportacao_plano.md)
- [json/tests/synthetic/exportacao_ficticia.md](/json/tests/synthetic/exportacao_ficticia.md) (dados sintéticos)
- [reconciliation.py](/src/health_refund_assistant/reconciliation.py) (match de registros)

**Referência de documentação:** [plan_export.schema.md](/json/plan/schemas/plan_export.schema.md)

---

## Integração com Código

```python
from health_refund_assistant.json_contracts import carregar_schema_json, validar_contrato_json

# Carregar schema
schema = carregar_schema_json("plan_export.schema.json")

# Validar dados importados
validar_contrato_json(dados_importados, "plan_export.schema.json", origem="exportacao.json")
```

## Fluxo de Importação

1. **Entrada:** exportação JSON do plano de saúde
2. **Validação:** `plan_export.schema.json` valida estrutura
3. **Armazenamento:** [json/plan/imports/](/json/plan/imports/) (ver `exportacao_plano.md`)
4. **Uso:** Reconciliação busca matches entre notas e pedidos do plano
