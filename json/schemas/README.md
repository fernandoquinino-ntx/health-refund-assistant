# Índice de contratos JSON

Os schemas ficam junto aos respectivos processos, não nesta pasta. Eles definem
estrutura e tipos, mas não garantem que dados sejam verdadeiros ou seguros.

| Processo | Contratos e documentação |
|---|---|
| Extração VLM | [extraction/schemas](../extraction/schemas/README.md) |
| Conciliação, revisão e mapeamento | [reconciliation/schemas](../reconciliation/schemas/README.md) |
| Plano e estimativa de pagamento | [plan/schemas](../plan/schemas/README.md) |
| Estado e resposta do assistente | [documents/schemas](../documents/schemas/README.md) |
| Avaliação | [evaluation/schemas](../evaluation/schemas/README.md) |
| Fixtures de testes | [tests/schemas](../tests/schemas/README.md) |

O manifesto e o gabarito são contratos separados; o gabarito não é enviado ao
prompt. Consulte também o [catálogo](../../docs/70_documentation/05_json_catalogo.md).
