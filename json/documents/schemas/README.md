# Document State Schema

Schema para estado de processamento de documentos fiscais extraídos.

## Arquivo

### `notes_state.schema.json`
Contrato para armazenamento do estado de cada nota processada.

**Propósito:** Registra extração VLM, transformações, validações e histórico de processamento.

**Consumidores:**
- [pdf_processing.py](../../../src/health_refund_assistant/documents/pdf_processing.py)
- [json/documents/state/notas_extraidas.md](../state/notas_extraidas.md)

**Referência de documentação:** [notes_state.schema.md](notes_state.schema.md)

---

O estado completo é validado pelo processamento em lote, não cada objeto de nota
individualmente. O schema de [resposta do assistente](./assistant_answer.schema.md)
também fica neste diretório.

## Fluxo de Documento

1. **Entrada:** PDF de nota fiscal
2. **Processamento:** VLM extrai dados (resultado em `vlm_extraction.schema.json`)
3. **Armazenamento:** Estado salvo em [json/documents/state/](../state) com `notes_state.schema.json`
4. **Rastreamento:** Histórico preservado para auditoria e reprocessamento
