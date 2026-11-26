# Test Schemas

Schemas para dados de teste: casos de teste e ground truth.

## Arquivos

### `test_cases.schema.json`
Contrato para manifesto de casos de teste.

**Propósito:** Define documentos, perguntas, categorias e datas de referência para teste.

**Consumidores:**
- [json/tests/synthetic/casos_teste.md](../synthetic/casos_teste.md)
- [json/tests/templates/casos_teste.template.md](../templates/casos_teste.template.md)
- [tests/test_*.py](../../../tests) (testes automatizados)

**Referência de documentação:** [test_cases.schema.md](test_cases.schema.md)

---

### `test_gold.schema.json`
Contrato para gabarito (ground truth).

**Propósito:** Extração correta esperada para cada documento de teste; usado para avaliação determinística.

**Consumidores:**
- [json/tests/synthetic/gabarito.md](../synthetic/gabarito.md)
- [json/tests/templates/gabarito.template.md](../templates/gabarito.template.md)
- [case_evaluation.py](../../../src/toolbox/case_evaluation.py) (comparação contra VLM)
- [tests/test_*.py](../../../tests)

**Referência de documentação:** [test_gold.schema.md](test_gold.schema.md)

---

## Integração com Código

```python
from health_refund_assistant.core.json_contracts import carregar_schema_json, validar_contrato_json
from toolbox.test_paths import TEST_SCHEMAS

# Carregar schemas
test_cases = carregar_schema_json(TEST_SCHEMAS["test_cases.schema.json"])
test_gold = carregar_schema_json(TEST_SCHEMAS["test_gold.schema.json"])

# Validar dados de teste
validar_contrato_json(casos, TEST_SCHEMAS["test_cases.schema.json"], "casos_teste.json")
validar_contrato_json(gabarito, TEST_SCHEMAS["test_gold.schema.json"], "gabarito.json")
```

## Estrutura de Teste

1. **Manifesto:** `test_cases.schema.json` lista documentos e perguntas
2. **Ground Truth:** `test_gold.schema.json` contém respostas esperadas
3. **Dados:** [json/tests/synthetic/](../synthetic) com arquivos fictícios
4. **Templates:** [json/tests/templates/](../templates) com exemplos editáveis
