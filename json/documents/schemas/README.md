# Document State Schema

Schema para estado de processamento de documentos fiscais extraídos.

## Arquivo

### `notes_state.schema.json`
Contrato para armazenamento do estado de cada nota processada.

**Propósito:** Registra extração VLM, transformações, validações e histórico de processamento.

**Consumidores:**
- [pdf_processing.py](/src/health_refund_assistant/pdf_processing.py) `salvar_status()`
- [json/documents/state/notas_extraidas.md](/json/documents/state/notas_extraidas.md)

**Referência de documentação:** [notes_state.schema.md](/json/documents/schemas/notes_state.schema.md)

---

## Integração com Código

```python
from health_refund_assistant.json_contracts import validar_contrato_json

# Salvar estado de processamento
dados_nota = {
    "id": "...",
    "arquivo": "...",
    "extracao": {...},
    "timestamp": "...",
    # ...
}

validar_contrato_json(dados_nota, "notes_state.schema.json", caminho_arquivo.name)
```

## Fluxo de Documento

1. **Entrada:** PDF de nota fiscal
2. **Processamento:** VLM extrai dados (resultado em `vlm_extraction.schema.json`)
3. **Armazenamento:** Estado salvo em [json/documents/state/](/json/documents/state/) com `notes_state.schema.json`
4. **Rastreamento:** Histórico preservado para auditoria e reprocessamento
