# VLM Extraction Schemas

Schemas para extração de dados de documentos fiscais usando Visual Language Models.

## Arquivos

### `vlm_extraction.schema.json`
Contrato para extração de dados de nota fiscal em versões 1.0–3.0 do prompt VLM.

**Campos:** 10 campos estruturados (descrição, prestador, profissional, etc.)

**Usado por:**
- [vlm_extractor.py](/src/health_refund_assistant/vlm_extractor.py)
- [prompts/vlm_extractor/v1.0.md](/prompts/vlm_extractor/v1.0.md)
- [prompts/vlm_extractor/v1.1.md](/prompts/vlm_extractor/v1.1.md)
- [prompts/vlm_extractor/v2.0.md](/prompts/vlm_extractor/v2.0.md)
- [prompts/vlm_extractor/v3.0.md](/prompts/vlm_extractor/v3.0.md)

**Referência de documentação:** [vlm_extraction.schema.md](/json/extraction/schemas/vlm_extraction.schema.md)

---

### `vlm_extraction_v4.schema.json`
Contrato para extração de dados com 11 campos (versão 4.0+).

**Campos:** 11 campos, incluindo `data_atendimento` adicional para melhor rastreamento.

**Usado por:**
- [vlm_extractor.py](/src/health_refund_assistant/vlm_extractor.py) (prompt v4.0)
- [prompts/vlm_extractor/v4.0.md](/prompts/vlm_extractor/v4.0.md)

**Referência de documentação:** [vlm_extraction_v4.schema.md](/json/extraction/schemas/vlm_extraction_v4.schema.md)

---

## Integração com Código

Esquemas são carregados dinamicamente em `paths.py` via `resolve_schema(nome)`:

```python
from health_refund_assistant.paths import resolve_schema
from health_refund_assistant.json_contracts import carregar_schema_json

schema = carregar_schema_json("vlm_extraction.schema.json")
# Carregamento: JSON_ROOT / "extraction" / "schemas" / "vlm_extraction.schema.json"
```

Contexto completo é incluído na mensagem ao modelo:

```python
from health_refund_assistant.json_contracts import contexto_schema_para_prompt

contexto = contexto_schema_para_prompt("vlm_extraction.schema.json")
# Retorna: descrição, schema completo, e template JSON de exemplo
```
