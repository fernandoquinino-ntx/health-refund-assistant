# VLM Extraction Schemas

Schemas para extração de dados de documentos fiscais usando Visual Language Models.

## Arquivos

### `vlm_extraction.schema.json`
Contrato para extração de dados de nota fiscal em versões 1.0–3.0 do prompt VLM.

**Campos:** nove campos estruturados (descrição, prestador, registro, etc.).

**Usado por:**
- [vlm_extractor.py](../../../src/health_refund_assistant/documents/vlm_extractor.py)
- [prompts/vlm_extractor/v1.0.md](../../../prompts/vlm_extractor/v1.0.md)
- [prompts/vlm_extractor/v1.1.md](../../../prompts/vlm_extractor/v1.1.md)
- [prompts/vlm_extractor/v2.0.md](../../../prompts/vlm_extractor/v2.0.md)
- [prompts/vlm_extractor/v3.0.md](../../../prompts/vlm_extractor/v3.0.md)

**Referência de documentação:** [vlm_extraction.schema.md](vlm_extraction.schema.md)

---

### `vlm_extraction_v4.schema.json`
Contrato para extração de dados com 11 campos (versões 4.0 e 4.1).

**Campos:** 11 campos, incluindo `data_atendimento` adicional para melhor rastreamento.

**Usado por:**
- [vlm_extractor.py](../../../src/health_refund_assistant/documents/vlm_extractor.py) (prompts v4.0 e v4.1)
- [prompts/vlm_extractor/v4.0.md](../../../prompts/vlm_extractor/v4.0.md)
- [prompts/vlm_extractor/v4.1.md](../../../prompts/vlm_extractor/v4.1.md)

**Referência de documentação:** [vlm_extraction_v4.schema.md](vlm_extraction_v4.schema.md)

---

### `vlm_extraction_v4_2.schema.json`

Contrato do [prompt v4.2](../../../prompts/vlm_extractor/v4.2.md), que acrescenta
trechos informados pela IA para revisão humana. Consulte a
[documentação do contrato](vlm_extraction_v4_2.schema.md); os trechos não são
prova independente de que a imagem contém os dados.

## Integração com Código

Esquemas são carregados dinamicamente em `paths.py` via `resolve_schema(nome)`:

```python
from health_refund_assistant.core.paths import resolve_schema
from health_refund_assistant.core.json_contracts import carregar_schema_json

schema = carregar_schema_json("vlm_extraction.schema.json")
# Carregamento: JSON_ROOT / "extraction" / "schemas" / "vlm_extraction.schema.json"
```

Contexto completo é incluído na mensagem ao modelo:

```python
from health_refund_assistant.core.json_contracts import contexto_schema_para_prompt

contexto = contexto_schema_para_prompt("vlm_extraction.schema.json")
# Retorna: descrição, schema completo, e template JSON de exemplo
```
