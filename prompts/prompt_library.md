# Biblioteca de prompts

Os prompts são armazenados por componente e separados por versão.

```text
prompts/
├── prompt_library.md
├── vlm_extractor/
│   ├── v1.0.md
│   ├── v1.1.md
│   ├── v2.0.md
│   ├── v3.0.md
│   ├── v4.0.md
│   └── v4.1.md
├── reembolso_assistente/
│   ├── v1.0.md
│   └── v1.1.md
├── reembolso_status/
│   ├── v1.0.md
│   └── v1.1.md
├── revisao_documental/
│   └── v1.0.md
└── estimativa_pagamento/
    └── v1.0.md
```

## Convenção

- Uma pasta por código ou componente.
- Cada arquivo usa `vMAIOR.MENOR.md`.
- O extrator e a interface selecionam a maior versão numérica por padrão; o
  mapeamento usa uma versão padrão definida no código.
- Uma versão específica pode ser selecionada pela interface ou pelos argumentos
  apropriados de cada comando.
- Nunca sobrescrever uma versão publicada; criar uma nova versão para alterações.
- O código acrescenta o schema e um modelo gerado do JSON correspondente em
  `json/`. Os valores do modelo são ilustrativos; não devem ser tratados como fatos.
  Versões históricas podem conter formatos ou exemplos escritos no próprio prompt
  para preservar seu conteúdo. Para reproduzir uma comparação anterior, fixe também
  o commit do código, pois o texto de contexto do schema é acrescentado em tempo
  de execução e pode mudar entre commits.

## `vlm_extractor`

| Versão | Arquivo | Hipótese / evolução |
|---|---|---|
| v1.0 | [vlm_extractor/v1.0.md](./vlm_extractor/v1.0.md) | Baseline: extrair os campos fiscais originalmente previstos. |
| v1.1 | [vlm_extractor/v1.1.md](./vlm_extractor/v1.1.md) | Descrição do serviço e CRM/CRN explícito; `null` para ausência e sem inferências. |
| v2.0 | [vlm_extractor/v2.0.md](./vlm_extractor/v2.0.md) | Dois exemplos Few-Shot completos, critérios mensuráveis de legibilidade e observação visual curta. |
| v3.0 | [vlm_extractor/v3.0.md](./vlm_extractor/v3.0.md) | Regras compactas para modelo 7B e delimitação de conteúdo visual não confiável contra prompt injection. |
| v4.0 | [vlm_extractor/v4.0.md](./vlm_extractor/v4.0.md) | Acrescenta data de atendimento e nome do profissional, mantendo os campos anteriores. |
| v4.1 | [vlm_extractor/v4.1.md](./vlm_extractor/v4.1.md) | Mantém as instruções da v4.0 sem repetir o objeto JSON; o código fornece o contrato. |

As versões v1.0 e v1.1 são preservadas sem edição. O extrator seleciona a versão
mais recente por padrão, mas as comparações acadêmicas devem fixar explicitamente
cada versão para manter a mesma bateria.

### Hipóteses testáveis

- **v1.0 → v1.1:** regras explícitas de ausência e não inferência devem melhorar
  descrição e registro profissional.
- **v1.1 → v2.0:** dois exemplos Few-Shot e critérios operacionais para
  `imagem_legivel` e `observacao_visual` devem reduzir variação de formato e
  inconsistências nos casos incompletos/ilegíveis.
- **v2.0 → v3.0:** instruções negativas concisas e a marcação
  `<documento_nao_confiavel>` devem reduzir a taxa de respostas alteradas por
  conteúdo adversarial no documento sem prejudicar a extração normal.
- **v3.0 → v4.0:** extração explícita da data de atendimento e do nome do profissional
  deve permitir avaliar prazo e campos incompletos sem confundir emissão e atendimento.
- **v4.0 → v4.1:** hipótese de que fornecer o formato somente pelo código mantenha
  a extração com menos duplicação. Ainda não há resultado medido para a v4.1.

### Contrato de saída

As versões v1.0 a v3.0 retornam exatamente nove campos: `numero_documento`, `prestador`,
`cnpj_cpf_prestador`, `valor_total`, `data_emissao`, `descricao_servico`,
`registro_profissional`, `imagem_legivel` e `observacao_visual`. A saída é validada
no código mesmo quando a API rejeita `json_schema`. As versões v4.0 e v4.1 acrescentam
`data_atendimento` e `nome_profissional`, mantendo todos os outros campos. O
processamento usa `GPT-6 Luna` pela API OpenAI e envia a imagem do documento para esse
serviço; não execute com dados reais sem revisar os requisitos de privacidade
aplicáveis.

Os prompts v1.0–v3.0 declaram o contrato
[`json/extraction/schemas/vlm_extraction.schema.json`](../json/extraction/schemas/vlm_extraction.schema.json);
v4.0 e v4.1 usam
[`json/extraction/schemas/vlm_extraction_v4.schema.json`](../json/extraction/schemas/vlm_extraction_v4.schema.json).
Cada documentação Markdown do schema referencia de volta as versões de prompt que o
utilizam. O extrator carrega o arquivo correspondente pela versão, inclui o schema e
um template JSON na mensagem de sistema e também usa o contrato no `response_format`
e na validação da resposta.

### Resultados comparativos

Resultados abaixo são da execução real anterior à migração, com `qwen2.5-vl-7b-instruct`
no LM Studio. Eles não representam o desempenho de `GPT-6 Luna`; execute novamente
após configurar `OPENAPI_TOKEN`. Não use placares hipotéticos como evidência.

| Versão | Modelo avaliado | Casos corretos / 15 | Acurácia por campo | Falhas críticas | Resultado |
|---|---|---:|---:|---:|---|
| v1.0 | Qwen2.5-VL-7B-Instruct | 13/15 (86,7%) | 97,8% | 0 | Aprovado |
| v1.1 | Qwen2.5-VL-7B-Instruct | 13/15 (86,7%) | 97,8% | 0 | Aprovado |
| v2.0 | Qwen2.5-VL-7B-Instruct | 13/15 (86,7%) | 98,5% | 0 | Aprovado |
| v3.0 | Qwen2.5-VL-7B-Instruct | 12/15 (80,0%) | 97,0% | 0 | Reprovado |

Os relatórios históricos do Qwen são registros de execuções anteriores e não fazem
parte do dataset versionado. Novas execuções com OpenAI devem ser salvas em
`json/evaluation/reports/v1.0.json` até `json/evaluation/reports/v4.1.json`. A v3.0 histórica ficou abaixo
do limiar inicial de 85%; as execuções atuais devem ser medidas novamente com o
modelo OpenAI.

### Caso de uso registrado: descrição e registro profissional

O extrator observa a descrição do serviço médico e identifica CRM ou CRN somente
quando aparecem explicitamente na imagem.

- `descricao_servico`: descrição visível do atendimento, como consulta, retorno,
  exame ou procedimento.
- `registro_profissional`: registro CRM/CRN explícito, preservando conselho, número
  e UF quando impressos.
- Ambos retornam `null` quando não houver informação explícita.
- Não inferir CRM/CRN ou tipo de atendimento pelo nome, prestador ou especialidade.

## `reembolso_status`

| Versão | Arquivo | Status |
|---|---|---|
| v1.0 | [reembolso_status/v1.0.md](./reembolso_status/v1.0.md) | Histórico |
| v1.1 | [reembolso_status/v1.1.md](./reembolso_status/v1.1.md) | Padrão; formato fornecido pelo código. |

Prompt para propor o mapa entre schemas uma única vez. A entrada deve conter apenas
nomes de campos, caminhos e tipos, sem valores dos registros.
O comando `python -m health_refund_assistant.plan.mapping` valida os caminhos propostos e salva um
arquivo de proposta separado; ele nunca substitui o mapeamento ativo.
O código usa como contrato de resposta
[`json/reconciliation/schemas/mapping_proposal.schema.json`](../json/reconciliation/schemas/mapping_proposal.schema.json);
o código carrega e inclui o schema e um template JSON na mensagem enviada ao modelo.
O schema e sua documentação apontam de volta para este prompt. Após validar os
caminhos, o código mescla a proposta na configuração definida por
[`json/reconciliation/schemas/mapping_config.schema.json`](../json/reconciliation/schemas/mapping_config.schema.json).

## `reembolso_assistente`

| Versão | Arquivo | Hipótese / finalidade |
|---|---|---|
| v1.0 | [reembolso_assistente/v1.0.md](./reembolso_assistente/v1.0.md) | Responder à pergunta do usuário usando apenas evidências determinísticas; não inferir pagamento, cobertura ou ausência de pedido fora do período exportado. |
| v1.1 | [reembolso_assistente/v1.1.md](./reembolso_assistente/v1.1.md) | Considerar a estimativa validada de processamento e distinguir do prazo de envio simulado. |

O assistente de resposta é independente do extrator. A interface permite escolher a
versão de cada componente separadamente e fornece ao prompt conversacional os campos
extraídos e os resultados calculados; não envia o gabarito do benchmark.
Para revisão, estimativa e resposta, o Python também acrescenta ao prompt o schema
completo e o modelo gerado, além de enviá-lo como formato de saída à API.
Como guardrail fixo, a aplicação acrescenta a qualquer versão da resposta uma
instrução para usar somente a estimativa validada e não analisar prazo de envio
para pedido localizado. A versão histórica do arquivo permanece inalterada.

## `revisao_documental`

O [v1.0](./revisao_documental/v1.0.md) orienta a revisão consultiva da imagem
e dos dados extraídos. A saída segue o
[contrato de revisão](../json/reconciliation/schemas/document_review.schema.md).

## `estimativa_pagamento`

O [v1.0](./estimativa_pagamento/v1.0.md) recebe data de submissão e referência e
retorna o [contrato de estimativa](../json/plan/schemas/payment_estimate.schema.md).
O cálculo é conferido em Python; somente pedidos com correspondência forte e
status adequado são considerados. Fins de semana são excluídos, feriados não.
A estimativa de cinco dias foi informada pelo usuário e não foi verificada com
o plano. Uma falha ou divergência interrompe a resposta.
