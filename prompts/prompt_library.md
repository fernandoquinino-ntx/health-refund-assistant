# Biblioteca de prompts

Os prompts são armazenados por componente e separados por versão.

```text
prompts/
├── prompt_library.md
├── vlm_extractor/
│   ├── v1.0.txt
│   ├── v1.1.txt
│   ├── v2.0.txt
│   ├── v3.0.txt
│   └── v4.0.txt
├── reembolso_assistente/
│   └── v1.0.txt
├── reembolso_status/
│   └── v1.0.txt
```

## Convenção

- Uma pasta por código ou componente.
- Cada arquivo usa `vMAIOR.MENOR.txt`.
- O código carrega a maior versão numérica por padrão.
- Uma versão específica pode ser selecionada pelo argumento `prompt_version`.
- Nunca sobrescrever uma versão publicada; criar uma nova versão para alterações.

## `vlm_extractor`

| Versão | Arquivo | Hipótese / evolução |
|---|---|---|
| v1.0 | [vlm_extractor/v1.0.txt](./vlm_extractor/v1.0.txt) | Baseline: extrair os campos fiscais originalmente previstos. |
| v1.1 | [vlm_extractor/v1.1.txt](./vlm_extractor/v1.1.txt) | Descrição do serviço e CRM/CRN explícito; `null` para ausência e sem inferências. |
| v2.0 | [vlm_extractor/v2.0.txt](./vlm_extractor/v2.0.txt) | Dois exemplos Few-Shot completos, critérios mensuráveis de legibilidade e observação visual curta. |
| v3.0 | [vlm_extractor/v3.0.txt](./vlm_extractor/v3.0.txt) | Regras compactas para modelo 7B e delimitação de conteúdo visual não confiável contra prompt injection. |
| v4.0 | [vlm_extractor/v4.0.txt](./vlm_extractor/v4.0.txt) | Acrescenta data de atendimento e nome do profissional, mantendo os campos anteriores. |

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

### Contrato de saída

As versões v1.0 a v3.0 retornam exatamente nove campos: `numero_documento`, `prestador`,
`cnpj_cpf_prestador`, `valor_total`, `data_emissao`, `descricao_servico`,
`registro_profissional`, `imagem_legivel` e `observacao_visual`. A saída é validada
no código mesmo quando a API rejeita `json_schema`. A v4.0 acrescenta
`data_atendimento` e `nome_profissional`, mantendo todos os outros campos. O
processamento usa `gpt-6-luna` pela API OpenAI e envia a imagem do documento para esse
serviço; não execute com dados reais sem revisar os requisitos de privacidade
aplicáveis.

Os prompts v1.0–v3.0 declaram o contrato
[`json/extraction/schemas/vlm_extraction.schema.json`](../json/extraction/schemas/vlm_extraction.schema.json);
v4.0 declara
[`json/extraction/schemas/vlm_extraction_v4.schema.json`](../json/extraction/schemas/vlm_extraction_v4.schema.json).
Cada documentação Markdown do schema referencia de volta as versões de prompt que o
utilizam. O extrator carrega o arquivo correspondente pela versão, inclui o schema e
um template JSON na mensagem de sistema e também usa o contrato no `response_format`
e na validação da resposta.

### Resultados comparativos

Resultados abaixo são da execução real anterior à migração, com `qwen2.5-vl-7b-instruct`
no LM Studio. Eles não representam o desempenho de `gpt-6-luna`; execute novamente
após configurar `OPENAPI_TOKEN`. Não use placares hipotéticos como evidência.

| Versão | Modelo avaliado | Casos corretos / 15 | Acurácia por campo | Falhas críticas | Resultado |
|---|---|---:|---:|---:|---|
| v1.0 | Qwen2.5-VL-7B-Instruct | 13/15 (86,7%) | 97,8% | 0 | Aprovado |
| v1.1 | Qwen2.5-VL-7B-Instruct | 13/15 (86,7%) | 97,8% | 0 | Aprovado |
| v2.0 | Qwen2.5-VL-7B-Instruct | 13/15 (86,7%) | 98,5% | 0 | Aprovado |
| v3.0 | Qwen2.5-VL-7B-Instruct | 12/15 (80,0%) | 97,0% | 0 | Reprovado |

Os relatórios históricos do Qwen são registros de execuções anteriores e não fazem
parte do dataset versionado. Novas execuções com OpenAI devem ser salvas em
`json/evaluation/reports/v1.0.json` até `json/evaluation/reports/v4.0.json`. A v3.0 histórica ficou abaixo
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
| v1.0 | [reembolso_status/v1.0.txt](./reembolso_status/v1.0.txt) | Atual |

Prompt para propor o mapa entre schemas uma única vez. A entrada deve conter apenas
nomes de campos, caminhos e tipos, sem valores dos registros.
O comando `python -m health_refund_assistant.mapping` valida os caminhos propostos e salva um
arquivo de proposta separado; ele nunca substitui o mapeamento ativo.
O prompt declara como contrato de resposta
[`json/reconciliation/schemas/mapping_proposal.schema.json`](../json/reconciliation/schemas/mapping_proposal.schema.json);
o código carrega e inclui o schema e um template JSON na mensagem enviada ao modelo.
O schema e sua documentação apontam de volta para este prompt. Após validar os
caminhos, o código mescla a proposta na configuração definida por
[`json/reconciliation/schemas/mapping_config.schema.json`](../json/reconciliation/schemas/mapping_config.schema.json).

## `reembolso_assistente`

| Versão | Arquivo | Hipótese / finalidade |
|---|---|---|
| v1.0 | [reembolso_assistente/v1.0.txt](./reembolso_assistente/v1.0.txt) | Responder à pergunta do usuário usando apenas evidências determinísticas; não inferir pagamento, cobertura ou ausência de pedido fora do período exportado. |

O assistente de resposta é independente do extrator. A interface permite escolher a
versão de cada componente separadamente e fornece ao prompt conversacional os campos
extraídos e os resultados calculados; não envia o gabarito do benchmark.
