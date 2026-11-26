# Evaluation Schema

Schema para relatórios de avaliação de qualidade do VLM Extractor.

## Arquivo

### `vlm_evaluation_report.schema.json`
Contrato para relatório de desempenho do modelo na extração de dados.

**Propósito:** Compara extrações VLM contra ground truth (gabarito) e gera métricas.

**Consumidores:**
- [evaluation.py](/src/health_refund_assistant/evaluation.py)
- [json/evaluation/reports/avaliacao.md](/json/evaluation/reports/avaliacao.md)

**Referência de documentação:** [vlm_evaluation_report.schema.md](/json/evaluation/schemas/vlm_evaluation_report.schema.md)

---

## Integração com Código

```python
from health_refund_assistant.core.json_contracts import carregar_schema_json

# Carregar schema para validação
schema = carregar_schema_json("vlm_evaluation_report.schema.json")
```

## Fluxo de Avaliação

1. **Entrada:** Extrações VLM (IDs de documentos)
2. **Comparação:** Match contra ground truth ([test_gold.schema.json](/json/tests/schemas/test_gold.schema.json))
3. **Métricas:** Calcula precisão, recall, F1-score por campo
4. **Saída:** Relatório em [json/evaluation/reports/](/json/evaluation/reports/) validado por `vlm_evaluation_report.schema.json`
