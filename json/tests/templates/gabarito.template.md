# `gabarito.template.json`

Template-fonte versionado do *ground truth* dos cenários. O gerador o copia para
`json/tests/synthetic/gabarito.json`; o avaliador compara a saída do modelo com esses
valores.

- **Contrato:** [test_gold.schema.json](../schemas/test_gold.schema.json).
- **Privacidade:** use apenas valores fictícios.
- **Segurança:** nunca incluir este arquivo no prompt ou na solicitação ao modelo.
