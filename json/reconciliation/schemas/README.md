# Reconciliation Schemas

Schemas para conciliação de notas fiscais e propostas de mapeamento de campos.

## Arquivos

### `mapping_config.schema.json`
Contrato para configuração versionada de mapeamento de campos.

**Propósito:** Define caminhos dos campos de nota e pedido, tolerâncias para conciliação.

**Consumidores:**
- [reconciliation.py](/src/health_refund_assistant/reconciliation.py)
- [mapping.py](/src/health_refund_assistant/mapping.py)
- [json/config/mapeamento_reembolsos.json](/json/config/mapeamento_reembolsos.json)

**Referência de documentação:** [mapping_config.schema.md](/json/reconciliation/schemas/mapping_config.schema.md)

---

### `mapping_proposal.schema.json`
Contrato para proposta de mapeamento automática gerada pelo modelo.

**Propósito:** Estrutura de saída do prompt de proposta de mapeamento (reembolso_status/v1.0.md).

**Usado por:**
- [mapping.py](/src/health_refund_assistant/mapping.py) `build_proposal()`
- [prompts/reembolso_status/v1.0.md](/prompts/reembolso_status/v1.0.md)

**Referência de documentação:** [mapping_proposal.schema.md](/json/reconciliation/schemas/mapping_proposal.schema.md)

---

### `reconciliation_report.schema.json`
Contrato para relatório final de conciliação.

**Propósito:** Resultado da reconciliação com candidatos de match, notas não reconhecidas, etc.

**Consumidores:**
- [reconciliation.py](/src/health_refund_assistant/reconciliation.py) `gerar_relatorio()`
- [json/reconciliation/reports/conciliacao.md](/json/reconciliation/reports/conciliacao.md)

**Referência de documentação:** [reconciliation_report.schema.md](/json/reconciliation/schemas/reconciliation_report.schema.md)

---

## Integração com Código

Esquemas são carregados dinamicamente:

```python
from health_refund_assistant.json_contracts import carregar_schema_json, contexto_schema_para_prompt

config = carregar_schema_json("mapping_config.schema.json")
proposal = carregar_schema_json("mapping_proposal.schema.json")

# Para prompts que geram saída JSON:
contexto = contexto_schema_para_prompt("mapping_proposal.schema.json")
# Inclui schema completo + template JSON na mensagem do modelo
```

## Fluxo de Conciliação

1. **Leitura:** `mapping_config.schema.json` carrega configuração de mapeamento
2. **Proposta:** Modelo gera output validado por `mapping_proposal.schema.json`
3. **Relatório:** Conciliação produz resultado em `reconciliation_report.schema.json`
