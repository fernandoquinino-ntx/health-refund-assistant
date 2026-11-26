# Evaluation Schema

Schema para relatórios de avaliação de qualidade do VLM Extractor.

## Arquivo

### `vlm_evaluation_report.schema.json`
Contrato para relatório de desempenho do modelo na extração de dados.

**Propósito:** Compara extrações VLM contra ground truth (gabarito) e gera métricas.

**Consumidores:**
- [case_evaluation.py](../../../src/toolbox/case_evaluation.py)
- [json/evaluation/reports/avaliacao.md](../reports/avaliacao.md)

**Referência de documentação:** [vlm_evaluation_report.schema.md](vlm_evaluation_report.schema.md)

---

## Integração com Código

```python
from health_refund_assistant.core.json_contracts import carregar_schema_json
from toolbox.test_paths import TEST_SCHEMAS

# Carregar schema para validação
schema = carregar_schema_json(TEST_SCHEMAS["vlm_evaluation_report.schema.json"])
```

## Fluxo de Avaliação

1. **Entrada:** Extrações VLM (IDs de documentos)
2. **Comparação:** Match contra ground truth ([test_gold.schema.json](../../tests/schemas/test_gold.schema.json))
3. **Métricas:** Calcula acurácia por campo e por caso e falhas críticas
4. **Saída:** Relatório em [json/evaluation/reports/](../reports) validado por `vlm_evaluation_report.schema.json`
