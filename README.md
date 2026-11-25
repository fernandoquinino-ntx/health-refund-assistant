# 🩺 Assistente Inteligente de Conciliação e Acompanhamento de Reembolsos de Saúde

> Projeto Final — MBA em AI-Engineering & Multi-Agents
> **Disciplina:** Advanced Generative AI
> **Professor:** Eron Cavalcante
> **Integrantes:** [Nome 1], [Nome 2], [Nome 3]

## Conteúdo

- [Visão geral e problema](#visão-geral-e-problema)
- [Proposta de solução](#proposta-de-solução)
- [Arquitetura e pipeline](#arquitetura-e-pipeline)
- [Arquivos e dados de conciliação](#arquivos-e-dados-de-conciliação)
- [Instalação](#instalação)
- [Execução](#execução)
- [GitHub Codespaces](#github-codespaces)
- [Biblioteca e evolução dos prompts](#biblioteca-e-evolução-dos-prompts)
- [Avaliação e casos de teste](#avaliação-e-casos-de-teste)
- [Segurança, privacidade e LGPD](#segurança-privacidade-e-lgpd)
- [Limitações e trabalhos futuros](#limitações-e-trabalhos-futuros)

## Visão geral e problema





O acompanhamento de solicitações de reembolso de planos de saúde é descentralizado. O
usuário do plano pode iniciar pedidos de reembolso por e-mail ou WhatsApp atraves da sua concierge que abre o pedido diretamente no site do plano de saude. O usuario envia uma nota, e muitas vezes nao organiza o armazenamento dessa nota ou receibo, o usuario tem que ficar verificando n oportal do plano, e quando tem muitos ele acaba se perdendo. esse programa visa em perguntar se um reembolso foi pedido, enviando a nota fiscal. se a nota fiscal nao tiver um registro de pedido de reembolso o assistente vai falar, se tiver um epdido e foi pago , o assistente tambem vai falar, se ele foi pago parcial tambem, ou se teve uma devolutiva. esse programa tera como dataset os pedidos de reembolsos exportados do site do plano de saude e atualizados, porem ele deve ficar atento se a nota fiscal for superior a data que ele tem informacoes , ele devera falar que nao foi importado refernete aquele dias. para evitar que no meio do dia faca um epdido de reembolso ele sempre ira importar d -1. entao ele so pode checar notas d-2


 armazenar notas e recibos em
pastas e receber atualizações no portal ao longo de semanas, por exemplo: solicitação
aberta, pendência de documento, reembolso pago ou recusa/glosa de valor. Sem cruzar
essas fontes, é difícil saber quais documentos já foram submetidos, quais pedidos
estão pendentes e quanto foi efetivamente pago.

O projeto busca responder duas perguntas:

- Quais notas locais têm um possível pedido correspondente na exportação do plano?
- Quais pedidos foram pagos, parcialmente pagos, recusados ou ainda estão pendentes?

Uma ausência de correspondência na exportação não comprova que o pedido nunca foi
enviado: a exportação pode não incluir o período ou beneficiários relevantes.

## Proposta de solução

Uma aplicação Streamlit que combina extração visual pela API OpenAI, exportações
locais do portal, conciliação determinística e uma resposta conversacional:

- **Coleta do portal:** uma extensão Chrome navega pelo portal Care Plus e exporta
  pedidos, status e período consultado em JSON. O usuário importa a exportação pela
  interface web.
- **Extração visual:** o `gpt-6-luna` da OpenAI recebe uma imagem da primeira página
  dos PDFs e extrai prestador, documento, valor, data, serviço e CRM/CRN. O conteúdo
  do documento é enviado à API OpenAI; veja os cuidados de privacidade abaixo.
- **Mapeamento de campos:** um comando opcional pede ao modelo local uma proposta de
  correspondência entre schemas. A proposta usa nomes e tipos de campos, é validada e
  exige revisão humana. O mapeamento atualmente ativo foi revisado manualmente.
- **Conciliação:** o Python compara notas e pedidos sem novas chamadas de IA e gera
  correspondências candidatas explicáveis para revisão. Não confirma automaticamente
  que uma nota foi enviada ou que houve pagamento.
- **Assistente:** o usuário escolhe separadamente o prompt de extração e o prompt
  conversacional, envia um PDF e escreve uma pergunta. A resposta em linguagem natural
  usa apenas os resultados estruturados da análise.

## Arquitetura e pipeline

```text
data/incoming/*.pdf ──> Streamlit ──> OpenAI VLM + prompt selecionado
                                      │
extension ──> JSON de exportação ────┤
                                      v
                         análise determinística em Python
                         (campos, período, prazo simulado,
                          candidatos e status financeiro)
                                      │
                         OpenAI chat + prompt selecionado
                                      v
                         resposta à pergunta do usuário
```

### Arquivos e dados de conciliação

| Caminho | Conteúdo e finalidade |
|---|---|
| `data/incoming/` | PDFs locais aguardando processamento manual ou em lote |
| `data/processed/` e `data/failed/` | PDFs processados ou que precisam de revisão/reprocessamento |
| `json/plan/imports/` | Cópias das exportações JSON importadas pela interface |
| `json/documents/state/notas_extraidas.json` | Estado com extrações do processamento em lote |
| `json/evaluation/reports/` e `json/reconciliation/reports/` | Relatórios locais separados por processo |
| `data/sinteticos/documentos/` | PDFs 100% fictícios usados na bateria |
| `json/tests/synthetic/` | Manifesto, gabarito e exportação sintética |
| `json/config/mapeamento_reembolsos.json` | Mapeamento ativo dos campos das notas e dos pedidos |
| `json/schemas/` | Contratos JSON Schema; cada contrato tem documentação ao lado |
| `json/tests/templates/` | Templates-fonte do manifesto e do gabarito |
| `prompts/vlm_extractor/` | Prompts versionados de extração visual |
| `prompts/reembolso_assistente/` | Prompts versionados de resposta conversacional |

### Tipos de arquivo JSON

Todos os JSONs mantidos pela aplicação ficam centralizados em [`json/`](./json/), com
subpastas por processo. O [catálogo JSON](./docs/json_catalogo.md) mostra cada caminho,
finalidade, produtor/consumidor, schema e documentação Markdown.

**Fluxo dos dados:** ao importar uma exportação do plano pela interface, a aplicação
guarda uma cópia em `json/plan/imports/`. No processamento em lote, os dados extraídos
das notas ficam em `json/documents/state/notas_extraidas.json` e o PDF é movido para
`data/processed/` ou `data/failed/`. A análise pontual de um PDF enviado pelo navegador
não persiste a extração.

A exportação do portal contém informações gerais como período e beneficiários e uma
lista `reembolsos`. Cada pedido pode incluir número de sinistro, prestador,
beneficiário, status, datas de solicitação/realização/pagamento, valores solicitados e
reembolsados, descrição e procedimento. O mapeamento configura os caminhos usados pelo
conciliador; não trata número de nota como número de sinistro nem confunde data de
emissão com data de realização do serviço.

O mapa completo das responsabilidades, com um módulo Python por funcionalidade,
está em [docs/estrutura_projeto.md](./docs/estrutura_projeto.md).

## Decisões técnicas

- **Inferência visual:** o extrator usa `gpt-6-luna` pela API OpenAI, com entrada de
  imagem e saída estruturada. A URL padrão é `https://api.openai.com/v1`; pode ser
  substituída por `OPENAI_BASE_URL`. Configure a chave exclusivamente na variável de
  ambiente `OPENAPI_TOKEN`. Veja a
  [documentação do modelo](https://developers.openai.com/api/docs/models/gpt-6-luna).
- **Mapeamento de schemas:** `qwen/qwen3.8-27b` é o modelo configurado para gerar uma
  proposta opcional pelo LM Studio local. Uma alternativa pode ser escolhida com
  `--model`, mas toda proposta precisa passar por validação e revisão humana.
- **Conciliação sem IA:** depois de configurado o mapa, a comparação é feita por
  código Python; a similaridade de prestador/serviço, valores e datas gera evidências
  para revisão, não uma decisão automática.
- **Dependências da aplicação:** `streamlit` para a interface, `openai` para a API
  e `PyMuPDF` para converter a primeira página do PDF em imagem.

## Instalação

Requisitos: Python 3.10+, conexão com a internet e acesso à API OpenAI. Para
Codespaces, consulte [GitHub Codespaces](#github-codespaces). O LM Studio é opcional
para propor o mapeamento de schemas.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

O `requirements.txt` instala o pacote do projeto em modo editável; as dependências
principais e os metadados ficam centralizados em `pyproject.toml`.

Crie as pastas para as entradas locais e os resultados:

```bash
mkdir -p data/incoming data/processed data/failed json/plan/imports json/documents/state json/evaluation/reports json/reconciliation/reports
```

Configure o token da API na sessão atual do terminal sem escrevê-lo no histórico:

```bash
printf 'Token OpenAI: '
read -s OPENAPI_TOKEN
printf '\n'
export OPENAPI_TOKEN
```

O extrator usa o modelo `gpt-6-luna` por padrão. O token não deve ser salvo no
repositório, em arquivos versionados ou em relatórios. `OPENAPI_TOKEN` deve conter
uma chave de API válida, sem o prefixo `Bearer `; o nome da variável, uma senha do
ChatGPT ou uma chave local do LM Studio não são credenciais da API.
`OPENAI_BASE_URL` é opcional e, se omitida ou vazia, usa
`https://api.openai.com/v1`. Um endpoint alternativo também receberá a chave e os
documentos enviados; só o configure se for confiável.

## Execução

### Interface do assistente

Com `OPENAPI_TOKEN` configurado, inicie a aplicação:

```bash
.venv/bin/streamlit run app.py
```

Abra `http://localhost:8501`. Importe uma exportação JSON da extensão que contenha
`periodo.de`, `periodo.ate` (ou `inicio`/`fim`) e a lista `reembolsos`; exportações
sem período válido são rejeitadas. Depois selecione o PDF, as versões independentes
dos prompts e escreva a pergunta. O sistema extrai a primeira página, calcula os
fatos e só então chama o prompt de resposta. O prazo de 30 dias é uma simulação
configurável, não uma regra confirmada do plano.

### Fluxo opcional em lote

#### 1. Exportar pedidos do plano

Instale a extensão seguindo [extension/LEIAME.md](./extension/LEIAME.md), faça login
no portal e exporte os pedidos. A extensão salva JSON em Downloads; importe o arquivo
pela interface para armazená-lo em `json/plan/imports/`.

### 2. Processar novos PDFs

Coloque os PDFs em `data/incoming/`, configure `OPENAPI_TOKEN` e execute:

```bash
.venv/bin/python -m health_refund_assistant.pdf_processing
```

Após uma extração bem-sucedida, o programa move o PDF para `data/processed/` e o
renomeia usando a data de emissão, o número do documento e um sufixo aleatório
único, por exemplo `2025-01-15_NF-123_a1b2c3d4.pdf`. O nome original e o resultado
continuam registrados em `json/documents/state/notas_extraidas.json`. Se o processamento falhar,
o PDF vai para `data/failed/`.

O programa detecta cópias com o mesmo SHA-256 sem chamar o VLM novamente. Depois
da extração, também sinaliza documentos que tenham o mesmo CNPJ/CPF do prestador
e número da nota. Essas duplicatas são preservadas em
`data/processed/duplicatas/` e registradas na propriedade `duplicatas` do JSON;
não são incluídas como novas notas na conciliação. A segunda regra depende de
ambos os campos estarem legíveis. O nome do médico não é usado como identificador.

Para tentar novamente os PDFs em `data/failed/`:

```bash
.venv/bin/python -m health_refund_assistant.pdf_processing --reprocessar-falhas
```

O estado e as extrações ficam em `json/documents/state/notas_extraidas.json`. O processador usa a
versão mais recente do prompt `vlm_extractor`; informe `--prompt-version v1.1`
para fixar uma versão. `--forcar` reprocessa PDFs que ainda estejam na entrada.
Para avaliar prompts sem mover os PDFs de teste, use `--manter-originais`.

O argumento antigo `--pasta-pdfs` continua aceito como alias de `--entrada`, para
processar PDFs de outra pasta. Os registros JSON existentes permanecem compatíveis;
novos PDFs devem ser colocados em `data/incoming/`.

### 3. Conciliar

O mapeamento ativo está em `json/config/mapeamento_reembolsos.json`. Gere um relatório
usando a exportação mais recente:

```bash
.venv/bin/python -m health_refund_assistant.reconciliation
```

O relatório JSON é salvo em `json/reconciliation/reports/conciliacao.json`. Para escolher arquivos:

```bash
.venv/bin/python -m health_refund_assistant.reconciliation \
  --notas json/documents/state/notas_extraidas.json \
  --exportacao json/plan/imports/arquivo.json \
  --saida json/reconciliation/reports/conciliacao.json
```

**O projeto usa JSON para as exportações, dados intermediários e relatórios. Não gera
arquivos CSV.** “Sem correspondência nesta exportação” não prova que o pedido nunca
foi enviado; confirme que a exportação cobre o período e todos os beneficiários.

### Proposta de mapeamento por modelo local (opcional)

O mapa ativo foi revisado manualmente. Para pedir ao modelo uma proposta usando somente
schemas:

```bash
.venv/bin/python -m health_refund_assistant.mapping --model qwen/qwen3.8-27b
```

A proposta fica em `json/config/mapeamento_reembolsos.proposta.json`. O comando verifica
que os caminhos existem e não substitui o mapeamento ativo. Revise a proposta antes
de promovê-la. A geração automática não é garantida: se o modelo não retornar JSON
válido, o comando apresenta erro e não ativa o resultado.

Antes de executar essa etapa opcional, carregue `qwen/qwen3.8-27b` no LM Studio (ou
informe o ID de outro modelo compatível em `--model`). O processamento VLM dos PDFs
usa a API OpenAI e não depende do LM Studio.

## Biblioteca e evolução dos prompts

Os prompts ficam em `prompts/`, separados por componente e versão. O extrator escolhe
a maior versão numérica e registra a versão usada em `_meta.prompt_version`.

| Componente | Versões presentes | Evolução documentada |
|---|---|---|
| `vlm_extractor` | v1.0–v4.0 | Extração, Few-Shot, defesa contra injeção e datas/profissional para avaliação de prazo |
| `reembolso_assistente` | v1.0 | Resposta conversacional ancorada em evidências calculadas |
| `reembolso_status` | v1.0 | Instruções para propor caminhos de campos usando schemas |

As versões v1.0 e v1.1 foram preservadas. A v2.0 adiciona dois exemplos Few-Shot,
critérios de legibilidade e observação visual; a v3.0 compacta regras e delimita o
conteúdo da imagem como dado não confiável. A v4.0 acrescenta data de atendimento e
nome do profissional, necessários à avaliação de completude e prazo. As versões v1.0
a v3.0 mantêm o contrato de nove campos; v4.0 tem contrato expandido de onze campos.
Consulte [prompts/prompt_library.md](./prompts/prompt_library.md) para as hipóteses.

## Avaliação e casos de teste

Para seguir um fluxo passo a passo de execução, comparação de prompts e registro de
métricas, consulte o [roteiro de avaliação](./docs/roteiro_avaliacao.md).

Gere os PDFs e arquivos JSON fictícios:

```bash
.venv/bin/python -m scripts.gerar_fixtures_sinteticas
```

O gerador cria 15 PDFs em `data/sinteticos/documentos/`, além de manifesto, gabarito
separado e exportação CarePlus fictícia em `json/tests/synthetic/`:

- C01–C04: pedido em análise, pagamentos integral/parcial e pedido recusado.
- C05–C07: nenhum pedido dentro do prazo, pedido existente após 30 dias e nenhum
  pedido localizado após 30 dias.
- C08–C10: nota sem nome do profissional, registro profissional ou descrição.
- C11–C13: data de atendimento ausente; emissão ausente com identificadores fiscais
  concorrentes; ambas as datas ausentes e valor líquido.
- C14–C15: tentativas de revelar instruções ou substituir prestador/valor; qualquer
  divergência nos campos fiscais é falha crítica.

Configure `OPENAPI_TOKEN` e compare as cinco versões contra os mesmos PDFs e
gabarito usando a API OpenAI:

```bash
.venv/bin/python -m health_refund_assistant.case_evaluation --prompt-version v1.0 \
  --saida json/evaluation/reports/v1.0.json
.venv/bin/python -m health_refund_assistant.case_evaluation --prompt-version v1.1 \
  --saida json/evaluation/reports/v1.1.json
.venv/bin/python -m health_refund_assistant.case_evaluation --prompt-version v2.0 \
  --saida json/evaluation/reports/v2.0.json
.venv/bin/python -m health_refund_assistant.case_evaluation --prompt-version v3.0 \
  --saida json/evaluation/reports/v3.0.json
.venv/bin/python -m health_refund_assistant.case_evaluation --prompt-version v4.0 \
  --saida json/evaluation/reports/v4.0.json
```

O avaliador usa `json/tests/synthetic/` e `data/sinteticos/documentos/` por padrão, compara campos com
tolerância monetária de R$ 0,01 e mantém o gabarito fora do prompt. A aprovação exige
15 casos executados, acurácia por caso de pelo menos 85% (limiar configurável) e zero
falhas críticas. As versões v1.0–v3.0 comparam os nove campos originais; v4.0 também
compara `data_atendimento` e `nome_profissional`. Resultados de precisão só devem ser
reportados depois de executar o VLM; os relatórios ficam em `json/evaluation/reports/` e não são
versionados. O prazo de 30 dias é somente uma regra simulada, não uma decisão
contratual.

Rode também os testes unitários determinísticos. Eles percorrem os 15 casos usando o
gabarito separado e a exportação sintética para conferir prazo, campos incompletos,
correspondência, status e evidência de pagamento, sem chamar a API. Isso é distinto do
benchmark de extração visual:

```bash
.venv/bin/python -m unittest discover -s tests -v
```

## GitHub Codespaces

O repositório inclui `.devcontainer/devcontainer.json`; ao criar um Codespace, ele
instala `requirements.txt` em `.venv` e encaminha a porta 8501. Para abrir a aplicação:

```bash
.venv/bin/streamlit run app.py --server.address 0.0.0.0
```

Configure `OPENAPI_TOKEN` em **GitHub → Settings → Secrets and variables →
Codespaces** antes de iniciar uma análise. Cada colaborador pode configurar seu
próprio segredo ou a organização pode disponibilizar um Codespaces secret ao
repositório. Nunca coloque a chave em `.env` versionado, notebook, prompt ou issue.

Todos podem colaborar nas versões em `prompts/` e rodar testes usando os fixtures
de `json/tests/synthetic/` e `data/sinteticos/documentos/`. **Não use nem envie PDFs
reais ou exportações reais nos Codespaces compartilhados.** `json/plan/imports/`,
relatórios e PDFs locais são
ignorados pelo Git. O workflow de CI gera os fixtures sintéticos e executa os testes
unitários em cada push e pull request; ele não chama a API OpenAI.

## Segurança, privacidade e LGPD

- O extrator envia a imagem da primeira página do PDF e o prompt à API OpenAI. Isso
  significa que documentos e dados pessoais/de saúde saem do computador; verifique
  a base legal, as políticas de retenção e as condições aplicáveis antes de usar
  documentos reais.
- A extensão só envia os dados ao LM Studio quando a opção correspondente estiver
  ativada. A URL é configurável; uma URL remota pode expor dados sensíveis.
- O gerador de mapeamento extrai e envia apenas nomes de campos e tipos, não os valores
  dos registros.
- A v3.0 delimita o conteúdo da imagem como dado não confiável e os casos C14/C15
  testam tentativas adversariais. Isso é uma mitigação, não uma garantia contra todas
  as formas de injeção.
- A aplicação não anonimiza nem remove identificadores dos documentos antes da
  extração. Os arquivos devem ser tratados como dados pessoais e de saúde sensíveis.
- O `.gitignore` exclui dados e saídas locais; somente fixtures JSON em
  `json/tests/synthetic/` e PDFs em `data/sinteticos/documentos/` podem ser
  versionados. Os exemplos gerados usam dados fictícios e não devem ser substituídos
  por notas reais.
- A chave `OPENAPI_TOKEN` é lida do ambiente e nunca deve ser registrada em código,
  logs ou Git. Use a bateria sintética para avaliação sem expor documentos reais.
- O uso da API não equivale a uma auditoria jurídica ou certificação de conformidade
  com a LGPD.

## Limitações e trabalhos futuros

- O conversor atual processa apenas a primeira página do PDF.
- A bateria sintética mede cenários controlados; a execução na API OpenAI ainda é
  necessária para produzir métricas observadas. O conversor lê apenas a primeira
  página.
- A conciliação usa similaridade textual e tolerâncias configuráveis; candidatos
  precisam de revisão humana e os limiares precisam ser calibrados com mais dados.
- Data de emissão da nota e data de realização do serviço são conceitos distintos;
  proximidade temporal é apenas evidência auxiliar.
- A exportação depende da extensão Care Plus e do período/beneficiários selecionados.
- Próximos passos acadêmicos: executar a bateria para v1.0, v1.1, v2.0, v3.0 e v4.0,
  revisar os resultados adversariais e documentar as métricas reais sem apresentar
  resultados hipotéticos.
