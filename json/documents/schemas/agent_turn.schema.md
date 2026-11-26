# Contrato da interpretação de turno do agente

Arquivo: `agent_turn.schema.json`.

Este contrato representa apenas a interpretação da intenção do usuário:

- `task`: próxima tarefa reconhecida.
- `note_reference`: número explícito informado pelo usuário, ou null.
- `missing`: próxima informação que o agente deve solicitar.
- `mensagem`: orientação opcional da IA, nunca usada como fato documental.

O modelo não recebe dados extraídos ou exportações como verdade. A resposta
determinística é construída pelas ferramentas existentes e validada separadamente.
