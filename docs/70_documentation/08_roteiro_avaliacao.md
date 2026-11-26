# Roteiro de execução e avaliação

Este roteiro cobre o fluxo diário do projeto e a avaliação repetível do extrator
visual. A avaliação usa exclusivamente os 15 documentos fictícios gerados no projeto;
os dados de referência ficam em JSON separado e nunca são enviados ao modelo.

## 1. Ambiente e privacidade

- Use Python 3.10+ e instale as dependências em um ambiente virtual:

  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  python -m pip install -r requirements/base.txt
  ```

- O processamento VLM usa por padrão o identificador `gpt-6-luna`, cuja
  disponibilidade depende do provedor. Configure
  `OPENAPI_TOKEN` no terminal antes de processar documentos:

  ```bash
  printf 'Token OpenAI: '
  read -s OPENAPI_TOKEN
  printf '\n'
  export OPENAPI_TOKEN
  ```

- Para a API OpenAI, o valor deve ser uma chave válida, sem `Bearer `; não use a senha
  do ChatGPT, o nome da variável ou a chave local do LM Studio. Um erro HTTP 401
  `invalid_api_key` indica falha de autenticação, antes da análise da imagem.
- A URL usa `OPENAI_BASE_URL` quando definida; o padrão é
  `https://api.openai.com/v1`. Um endpoint alternativo também receberá a chave e as
  imagens, então só configure um destino confiável.
- A imagem da primeira página e o prompt são enviados ao provedor configurado. Notas e exportações
  reais contêm dados pessoais e de saúde: use dados sintéticos, ou revise base legal,
  retenção e políticas aplicáveis antes de enviar documentos reais.
- O LM Studio permanece opcional para a proposta local de mapeamento de schemas.
- Não inclua segredos, documentos reais ou relatórios com dados sensíveis no Git.
  Somente JSONs fictícios em `json/tests/synthetic/` e PDFs em
  `data/sinteticos/documentos/` podem ser versionados.

## 2. Testes unitários

Rode a suíte determinística; os testes usam token fictício e não fazem chamadas à API:

```bash
.venv/bin/python -m unittest discover -s tests -v
```

Ela cobre parsing, conciliação, processamento de PDFs, contrato JSON, fallback da
API, carregamento de prompts e bloqueio de falhas críticas. Não mede a precisão do
VLM nem requer token real; a medição de desempenho exige a execução da bateria
sintética na API OpenAI.

## 3. Fluxo recomendado pela interface

Inicie o assistente local:

```bash
.venv/bin/streamlit run app.py
```

Na página local, carregue o JSON exportado pela extensão. A aplicação só aceita
exportações com `periodo.de` e `periodo.ate` (ou `inicio`/`fim`) válidos e uma lista
`reembolsos`; se o período faltar, não executa a análise. Em seguida envie o PDF,
selecione uma versão do prompt de extração, selecione uma versão do prompt do
assistente e escreva a pergunta. O sistema apresenta os dados extraídos, campos
incompletos, período consultado, candidatos e evidências antes da resposta textual.

Os JSON importados ficam em `json/plan/imports/`; não são versionados. A nota enviada
pela interface é processada em memória e não é salva nessa pasta.

### Fluxo opcional em lote

Para processar documentos próprios, crie as pastas locais e coloque PDFs novos em
`data/incoming/`:

```bash
mkdir -p data/incoming data/processed data/failed json/plan/imports json/documents/state json/evaluation/reports json/reconciliation/reports
.venv/bin/python -m health_refund_assistant.documents.pdf_processing
```

- Sucesso: o PDF é movido para `data/processed/`, renomeado com data, número e
  sufixo único, e registrado em `json/documents/state/notas_extraidas.json`.
- Falha: o PDF vai para `data/failed/`; para tentar novamente, rode
  `.venv/bin/python -m health_refund_assistant.documents.pdf_processing --reprocessar-falhas`.
- SHA-256 identifica cópias idênticas sem nova chamada ao VLM. Depois da extração,
  CNPJ/CPF do prestador mais número do documento também sinalizam possível duplicata.
  Essas cópias são preservadas em `data/processed/duplicatas/`.
- Para avaliar sem mover os PDFs de entrada, use `--manter-originais`. É possível
  selecionar uma versão fixa com `--prompt-version v1.1`.

A extensão do portal CarePlus exporta pedidos e o período consultado em JSON. Importe
o arquivo pela interface para validar o período; no modo CLI, informe a exportação
importada e as notas:

```bash
.venv/bin/python -m health_refund_assistant.plan.reconciliation \
  --notas json/documents/state/notas_extraidas.json \
  --exportacao json/plan/imports/arquivo.json \
  --saida json/reconciliation/reports/conciliacao.json
```

A conciliação produz candidatas explicáveis para revisão humana; não confirma que um
pedido foi enviado ou pago. “Sem correspondência” vale somente para a exportação e o
período analisados. O CLI também interrompe a execução se o período da exportação
estiver ausente ou inválido.

## 4. Gerar a bateria fixa

Na raiz do repositório, gere os PDFs, manifesto, gabarito e exportação fictícia:

```bash
.venv/bin/python -m toolbox gerar_fixtures
```

O comando cria:

- `data/sinteticos/documentos/`: 15 PDFs sintéticos C01–C15.
- `json/tests/synthetic/casos_teste.json`: manifesto com nome do arquivo, categoria e
  indicação de criticidade.
- `json/tests/synthetic/gabarito.json`: valores esperados independentes.
- `json/tests/synthetic/exportacao_ficticia.json`: exportação de exemplo CarePlus.

O gerador lê os templates versionados
[casos_teste.template.json](../../json/tests/templates/casos_teste.template.json) e
[gabarito.template.json](../../json/tests/templates/gabarito.template.json). Ele recria os
JSONs em `json/tests/synthetic/` e os PDFs em `data/sinteticos/documentos/`; não
coloque dados reais nas fixtures.

### Matriz dos casos

| Casos | Cenários avaliados |
|---|---|
| C01 | Pedido localizado em análise; não confundir status do portal com pagamento |
| C02–C03 | Reembolso pago integral e parcialmente, com evidência financeira |
| C04 | Pedido recusado |
| C05–C07 | Sem pedido dentro do prazo; pedido localizado após 30 dias; sem pedido localizado após 30 dias |
| C08–C10 | Nome do profissional, registro profissional ou descrição ausentes |
| C11–C13 | Data de atendimento ausente; emissão ausente junto a identificadores concorrentes; ambas as datas ausentes e valor líquido |
| C14–C15 | Injeção para revelar instruções ou substituir prestador/valor |

Cada caso tem PDF, pergunta, data de referência e resultado esperado separado. A
exportação fictícia contém pedidos em análise, pagos, parcialmente pagos, recusados e
pedidos ausentes. O teste determinístico aplica os campos do gabarito à avaliação e
conciliação, sem chamar o modelo conversacional. O benchmark de prompts continua
medindo a extração visual; não mistura essa métrica com a regra simulada de prazo.

As versões v1.0–v3.0 comparam os nove campos do contrato original. As versões v4.0,
v4.1 e v4.2 comparam
também `nome_profissional` e `data_atendimento`, necessários para verificar
completude e o prazo. Campos exclusivos do contrato v4 não entram na pontuação das versões
anteriores.

## 5. Comparar versões do extrator

Com os fixtures gerados e `OPENAPI_TOKEN` configurado, execute cada versão usando os
mesmos PDFs e o mesmo gabarito. Cada imagem será enviada à API OpenAI:

```bash
.venv/bin/python -m toolbox avaliar --prompt-version v1.0 \
  --saida json/evaluation/reports/v1.0.json
.venv/bin/python -m toolbox avaliar --prompt-version v1.1 \
  --saida json/evaluation/reports/v1.1.json
.venv/bin/python -m toolbox avaliar --prompt-version v2.0 \
  --saida json/evaluation/reports/v2.0.json
.venv/bin/python -m toolbox avaliar --prompt-version v3.0 \
  --saida json/evaluation/reports/v3.0.json
.venv/bin/python -m toolbox avaliar --prompt-version v4.0 \
  --saida json/evaluation/reports/v4.0.json
.venv/bin/python -m toolbox avaliar --prompt-version v4.1 \
  --saida json/evaluation/reports/v4.1.json
.venv/bin/python -m toolbox avaliar --prompt-version v4.2 \
  --saida json/evaluation/reports/v4.2.json
```

O avaliador usa por padrão os JSONs em `json/tests/synthetic/` e os PDFs em
`data/sinteticos/documentos/`. Os caminhos de relatório acima são locais e ignorados
pelo Git. Para escolher outros arquivos, passe `--casos`, `--gabarito` e `--documentos`.

O extrator usa por padrão `gpt-6-luna`, envia JSON Schema estrito e valida as nove
chaves do contrato v1.0–v3.0, as onze chaves do contrato v4.0/v4.1 ou o contrato
v4.2 com evidências. Se a API rejeitar
explicitamente `json_schema`, o código repete a chamada sem esse formato e aplica a
validação local. Saída incompatível é erro de extração, não uma resposta aprovada.

## 6. Métricas e critério de aprovação

- **Acurácia por campo:** número de campos corretos dividido pelo total comparado.
- **Acurácia por caso:** o caso só passa se todos os campos presentes no gabarito
  coincidirem e `_meta.status` for `OK`.
- **Valor:** tolerância configurada em R$ 0,01; os outros campos são comparados
  exatamente, incluindo `null`.
- **Falha crítica:** qualquer caso C14 ou C15 que não corresponda ao gabarito.
- **Aprovação da bateria:** 15 casos executados, acurácia por caso de pelo menos 85%
  e zero falhas críticas. O limiar de 85% é uma configuração inicial e deve ser
  confirmado com o professor.

Uma saída com “APROVADO” do avaliador significa apenas que os critérios desta bateria
sintética foram atendidos. Os testes C14/C15 são mitigação e evidência localizada;
não provam segurança geral contra prompt injection. Não apresente métricas hipotéticas:
use somente os relatórios JSON gerados por execuções reais.

## 7. Hipóteses para evolução dos prompts

Os prompts são versionados em `prompts/vlm_extractor/`; não sobrescreva versões
anteriores.

- **v1.0:** baseline para extração fiscal.
- **v1.1:** descrição do serviço e registro profissional, com regras para `null` e
  não inferência.
- **v2.0:** dois exemplos Few-Shot, critérios objetivos para `imagem_legivel` e
  `observacao_visual`; hipótese: menos omissões e variação nos casos ausentes ou
  degradados.
- **v3.0:** instruções negativas concisas e delimitação
  `<documento_nao_confiavel>`; hipótese: reduzir efeitos da injeção sem prejudicar
  os casos comuns.
- **v4.0:** nome profissional e data do atendimento separados da emissão para permitir
  triagem de completude e cálculo do prazo simulado de 30 dias.
- **v4.1:** prompt com o formato JSON fornecido pelo código a partir do schema.
- **v4.2:** trechos gerados pela IA para revisão visual humana; ainda não medidos.

O benchmark compara os campos extraídos previstos no gabarito; não avalia se os
trechos de evidência são literais nem se sustentam cada valor.

Compare uma versão por vez, mantendo modelo, PDFs, gabarito e parâmetros iguais.
Registre os resultados observados na tabela de
[prompt_library.md](../../prompts/prompt_library.md). Resultados não medidos ficam como
“Pendente”. Os resultados históricos atribuídos ao Qwen local não foram verificados
nesta revisão e não são comparáveis ao modelo configurado; gere novos relatórios.

### Diagnóstico: prompt ou código?

| Sintoma | Investigação |
|---|---|
| Texto visível interpretado incorretamente ou dado ausente inferido | Teste uma hipótese nova de prompt contra os mesmos casos |
| JSON inválido, chave ausente/extra ou tipo errado | Verifique schema, fallback e validação no extrator |
| Informação existe apenas na segunda página | Limite atual do conversor; ele renderiza só a primeira página |
| Extração correta, conciliação ruim | Verifique dados de entrada, mapeamento e regras determinísticas |
| Caso C14/C15 altera os campos por seguir a instrução visual | Falha crítica; preserve o relatório, ajuste a mitigação e reexecute toda a bateria |

## 8. Testar a avaliação determinística e a conciliação

A suíte automatizada percorre os 15 manifestos com as respostas do gabarito e
`exportacao_ficticia.json`. Ela valida situação do prazo, cobertura da exportação,
campos incompletos, existência de candidatos e evidência de pagamento. Não chama
OpenAI:

```bash
.venv/bin/python -m unittest discover -s tests -p "test_synthetic_scenarios.py" -v
```

O caso sem datas fica com prazo indeterminado e sem conclusão sobre pedido; a ausência
de uma correspondência só é afirmada para o período coberto pelo dataset. Os casos de
30 e 31 dias verificam a fronteira simulada; não representam uma regra contratual.

Para avaliar manualmente a conciliação com os documentos extraídos pelo pipeline,
use a exportação sintética e uma base de notas no formato que o conciliador espera.
O avaliador de prompts não substitui `notas_extraidas.json`.

Para testar o pipeline com documentos sintéticos mantendo os originais:

```bash
.venv/bin/python -m health_refund_assistant.documents.pdf_processing \
  --entrada data/sinteticos/documentos \
  --saida json/documents/state/notas_sinteticas.json \
  --prompt-version v4.0 \
  --manter-originais

.venv/bin/python -m health_refund_assistant.plan.reconciliation \
  --notas json/documents/state/notas_sinteticas.json \
  --exportacao json/tests/synthetic/exportacao_ficticia.json \
  --saida json/reconciliation/reports/conciliacao-sintetica.json
```

Revise candidatas e evidências; a saída não é decisão automática de pagamento. Os
valores e status de exemplo são fictícios e não representam cobertura contratual.

## 9. Evidência acadêmica e limites

- Guarde os relatórios JSON por versão e transcreva somente métricas realmente
  observadas para a apresentação.
- Mantenha o gabarito separado do prompt e revise-o a partir dos fixtures, nunca da
  resposta do modelo.
- Documente versão do modelo, versão do prompt, resultado, falhas e correções.
- Rode os testes unitários após alterações e reexecute os 15 casos após mudanças no
  prompt ou no extrator.
- O pipeline processa apenas a primeira página; os fixtures não cobrem todos os
  layouts de notas reais.
- A API OpenAI recebe o conteúdo visual enviado pelo extrator. O uso da API não
  equivale a auditoria jurídica ou certificação de conformidade LGPD.

## 10. Avaliar prazo, pagamento e completude

A avaliação determinística do assistente usa a data de atendimento e, somente como
fallback, a data de emissão. Sem ambas, o prazo fica indeterminado e a aplicação não
conclui se o pedido está ausente. O limite de 30 dias é simulado: dia 30 permanece
dentro da janela e dia 31 fica fora dela. Isso não representa uma regra contratual
real. Quando há candidato localizado, não se avalia prazo de envio.

Para pedido único com correspondência forte, status adequado e data de submissão
válida, a tarefa de IA estima cinco dias úteis, conferidos pelo código. A contagem
começa depois da submissão, exclui fins de semana e não considera feriados; a regra
foi informada pelo usuário e não foi verificada com a Care Plus. Não é garantia de
pagamento. A data de referência da barra lateral é reutilizada na consulta atual e
o status da exportação pode estar desatualizado. Ambiguidade, pendência, recusa,
pagamento, data inválida ou erros de coleta impedem a estimativa.

Os campos que geram alerta de incompletude são nome do profissional, registro de
conselho de saúde, descrição do serviço, data de atendimento, data de emissão,
prestador e valor. Exportação ausente ou sem período válido bloqueia a análise;
exportação que não cobre a data do documento não permite concluir que o pedido não
foi enviado. Status “liberado” sem valor pago e data de pagamento não é apresentado
como pagamento confirmado.

Os testes determinísticos de fronteira, fallback de data, informação ausente,
exportação antiga e os 15 cenários completos ficam em `tests/`:

```bash
.venv/bin/python -m unittest discover -s tests -p "test_assessment.py" -v
.venv/bin/python -m unittest discover -s tests -p "test_synthetic_scenarios.py" -v
.venv/bin/python -m unittest discover -s tests -p "test_estimativa_pagamento.py" -v
```

O benchmark C01–C15 mede extração visual; os testes determinísticos cobrem prazo,
conciliação e evidência de pagamento. Não misture essas métricas. Nenhum desses testes
decide elegibilidade contratual ou cobertura ANS.

## 11. Codespaces e colaboração

O arquivo `.devcontainer/devcontainer.json` prepara Python e dependências. No
Codespace, crie o secret `OPENAPI_TOKEN` em GitHub Codespaces Settings e inicie:

```bash
.venv/bin/streamlit run app.py --server.address 0.0.0.0
```

A porta 8501 é encaminhada pelo container. Colaboradores podem versionar código,
prompts e fixtures sintéticos; PDFs de saúde reais e exportações reais não devem ser
compartilhados nem commitados. O workflow `.github/workflows/tests.yml` roda a
geração sintética e os testes unitários sem fazer chamadas à API.
