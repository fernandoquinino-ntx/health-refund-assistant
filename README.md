# Assistente de reembolsos de saúde

Protótipo para consultar notas e recibos médicos diante de exportações do portal do
plano. O objetivo é apoiar a rastreabilidade quando documentos são enviados a uma
concierge e os pedidos são atualizados posteriormente no portal.

## Como funciona

1. Converse com o assistente em linguagem natural.
2. O agente interpreta a tarefa e solicita somente os anexos faltantes.
3. Envie uma nota fiscal ou recibo em PDF editável, PDF escaneado, JPG ou PNG.
   Quando necessário, envie a exportação JSON atual do plano.
4. GPT-6 Luna interpreta o pedido e sintetiza a resposta.
5. O modelo visual local ou remoto extrai campos estruturados da imagem.
6. Código determinístico concilia o documento, identifica campos e calcula prazo.
7. Uma tarefa separada revisa evidências e inconsistências visuais.
8. A interface apresenta o resultado resumido e mantém evidências detalhadas
   disponíveis em uma área recolhida.

Uma ausência na exportação não prova que o pedido nunca foi enviado. Confirme
resultados, exigências e prazos com o plano. A aplicação não envia pedidos.
O schema, os prompts e as regras reduzem riscos, mas não garantem proteção contra
instruções maliciosas, respostas incorretas ou vazamento.
Uma nova análise faz três chamadas à API: extração, revisão e resposta. Uma quarta
chamada é feita quando a estimativa de processamento pode ser calculada; nas
perguntas seguintes, a estimativa é calculada novamente nessas condições. A imagem
da primeira página é enviada na extração e novamente na revisão, com custo e
implicações de privacidade; use documentos sintéticos nos testes.

**Limitações importantes:** o prazo de envio de **30 dias é simulado**, configurável
na interface e não é analisado quando há pedido localizado. A estimativa de
processamento de **cinco dias úteis** foi informada pelo usuário e não foi verificada
com a Care Plus. Começa no primeiro dia útil após a submissão, exclui sábados e
domingos, mas não feriados; não é garantia de pagamento. Data futura ou ausente,
status inadequado, erros de coleta e correspondência incerta impedem a estimativa.
Registros conflitantes de um mesmo pedido também a impedem. Análises salvas antes
da verificação desses conflitos exigem reenviar o PDF e selecionar as exportações.
A regra de 365 dias e o corte D-2, mencionados em
documentos anteriores, ainda não estão implementados neste fluxo. Sem regras
contratuais verificadas, a elegibilidade é **não é possível avaliar**.

## Tarefas, entradas, saídas e conferência

| Tarefa | Entrada | Saída | Conferência |
|---|---|---|---|
| Extração VLM | Primeira página do PDF | Campos JSON | Schema e tipos validados localmente |
| Importação e conciliação | Exportação JSON e dados extraídos | Período, candidatos e cálculos | Schema, datas e regras determinísticas |
| Revisão documental por IA | Imagem, pergunta e evidências | [Revisão JSON](json/reconciliation/schemas/document_review.schema.md) | Schema e contradições básicas; revisão humana necessária |
| Estimativa de processamento por IA | Data de submissão e data de referência | [Estimativa JSON](json/plan/schemas/payment_estimate.schema.md) | Schema e comparação com contagem independente de dias úteis |
| Resposta por IA | Pergunta, histórico e evidências | [Resposta JSON](json/documents/schemas/assistant_answer.schema.md) | Schema local; não comprova a verdade do texto |
| Processamento em lote | PDFs | Extrações e erros por arquivo | Mesmo extrator e contrato; não avalia elegibilidade |
| Proposta de mapeamento | Estrutura dos dados, sem seus valores | Proposta JSON | Schema e caminhos existentes; revisão humana |
| Avaliação sintética | PDFs, casos e gabarito | Relatório e estado por caso | Validação de entrada e relatório; compara extração, não elegibilidade |

Em cada chamada de IA, o Python combina o prompt da tarefa com o schema JSON do
diretório correspondente em `json/` e um modelo gerado a partir dele. Na extração e
nas tarefas do chat, o schema também é enviado no `response_format`, quando
suportado; a resposta é validada localmente. Exemplos do modelo não são dados reais.

Exemplos sintéticos de interação:

| Tipo de interação | Entrada | Saída típica |
|---|---|---|
| Consultar status | Nota fiscal + exportação JSON | Status registrado e próximos dados solicitados |
| Confirmar pagamento | Número da nota + exportação JSON | Valor/status somente se houver registro |
| Verificar prazo | Nota ou data + referência | Prazo simulado ou indeterminado, com aviso |
| Revisar completude | JPG/PNG/PDF | Lista de campos ausentes ou ilegíveis |
| Tarefa desconhecida | Texto fora do catálogo | Pedido de esclarecimento e opções válidas |

Os detalhes completos ficam no [contrato central das tarefas](json/config/agent_tasks.json).

Falha de API ou saída inválida interrompe a resposta do chat; não é apresentada
como sucesso. Processamentos em lote e avaliações registram o estado por arquivo
ou caso. Uma conversa salva antes da revisão por IA precisa de novo PDF.

## Executar localmente ou em Codespaces

O projeto requer Python 3.10 ou superior. No Codespaces, o dev container executa
`make setup-codespace` na criação e `make run` ao iniciar. Para instalação local:

```bash
python3 -m venv .venv
make setup
```

Configure `OPENAPI_TOKEN` no ambiente ou como segredo do Codespaces. O código
não carrega `.env` automaticamente. `OPENAI_BASE_URL` é opcional; o identificador
padrão do modelo é `gpt-6-luna`, cuja disponibilidade e compatibilidade dependem
do provedor configurado. O nome de um modelo usado no Copilot não garante acesso
ao mesmo identificador pela API.

```bash
make run
```

Abra a porta `8501` no navegador. Ela é a porta HTTP local do Streamlit: a UI
carrega em `http://127.0.0.1:8501` localmente ou é encaminhada pelo Codespaces.
Converse normalmente e anexe uma nota PDF/imagem e, quando necessário, uma
exportação JSON do plano.

Comandos resumidos:

```bash
make help
make setup
make test
make test-agent
make ingest
make prepare-tasks
make label-studio
make build-dataset
make check-dataset
make train-mac
make convert
make build-extension
make clean
```

Os grupos de dependências ficam em [`requirements/`](requirements/). O Makefile
centraliza ambientes, testes, OCR, Label Studio, treinamento, conversão e build.

## Memória e privacidade

A aplicação possui autenticação local para testes, baseada em usuário e PIN com
hash PBKDF2. O arquivo `json/config/usuarios_locais.json` e as memórias em
`json/documents/state/usuarios/` são ignorados pelo Git. Cada usuário autenticado
recebe seu próprio arquivo de conversa e trilha de eventos. A autenticação local
não substitui identidade segura ou controle de produção.

O PDF não é salvo na memória; campos extraídos, perguntas e respostas podem conter
dados sensíveis. O botão **Apagar conversa local** remove somente o arquivo do
usuário autenticado, mas não remove exportações importadas nem dados enviados ao
provedor da API. Não compartilhe a porta do Codespace com dados reais.

## Rastreamento local

Cada interação registrada gera um evento em
`json/documents/state/traces/<usuario>/eventos.jsonl`. O evento inclui tarefa,
status, versões dos prompts, hashes de entrada/anexos, hash da saída, duração e
erro. PIN e texto bruto não são gravados. A aba **Auditoria local** mostra os
eventos recentes na interface. O JSONL é privado e ignorado pelo Git.

## Testes

```bash
make test
```

Os testes automatizados não comprovam que o modelo esteja disponível, que o
Codespace tenha sido iniciado, nem que as respostas reais estejam corretas.
O [workflow do GitHub](.github/workflows/tests.yml) executa a mesma suíte em
push, pull request ou acionamento manual, sem chamar a API. Ele usa as fixtures
de teste já versionadas, não os PDFs privados em `data/treinamento/`.

Para preparar seus próprios PDFs e anotar campos sem chamar uma API, consulte o
[guia de anotação de documentos](docs/40_testing/04_anotacao_documentos.md).

Para o fluxo visual foram verificados no Mac Tesseract **5.5.4** e o idioma
`por`. Versões ou dados de idioma diferentes podem alterar o OCR.

O fluxo implementado fica em `src/treinamento_visual/`: ingestão, rotulagem,
montagem do dataset, validação, treino LoRA no Mac e pipeline de GitHub Actions.
Os dados privados ficam em `data/treinamento/` e modelos em `models/`; ambos
são ignorados pelo Git.

Com as dependências de `requirements/treinamento.txt` instaladas no ambiente
isolado Python 3.12, coloque seus PDFs ou imagens JPG/PNG em
`data/treinamento/entrada/` e execute:

```bash
make ingest
```

O programa renderiza os PDFs a 300 DPI e preserva as dimensões das imagens,
aplicando sua orientação EXIF. As páginas ficam em
`data/treinamento/paginas/ocr_300dpi/`; palavras, coordenadas e linhas ficam em `data/treinamento/ocr/`, organizadas
por documento. Resultados existentes são preservados; erros detalhados ficam em
`data/treinamento/logs/ingestao.log`. Não compartilhe imagens, textos ou logs.
A pasta de OCR de cada documento contém `origem.json` para associá-la ao arquivo
de entrada; esse arquivo também é privado.
A reconstrução de colunas é aproximada e o OCR pode errar ou não encontrar
texto: revise visualmente cada página. O modelo visual recebe a imagem; o OCR
é apenas apoio.

Para verificar a instalação isolada do Label Studio com Sentry e analytics
desativados, execute:

```bash
make label-studio
```

O iniciador usa armazenamento local em `data/treinamento/label_studio/`,
desativa a consulta automática de versão, restringe o servidor a `127.0.0.1`
e executa o processo no sandbox de rede do macOS, permitindo conexões locais.
Ele não inicia o servidor em outros sistemas nem sem o sandbox.
Não execute o Label Studio diretamente: sua configuração padrão ativa o Sentry.
O sandbox cobre somente o processo do servidor; não isola o navegador nem impede
que outros serviços locais encaminhem dados. Não carregue documentos até concluir
a revisão de isolamento. A configuração em
`src/treinamento_visual/label/config.xml` define os campos e a transcrição por
região.
O comando abaixo prepara um JSON privado de tarefas sem carregar imagens no
Label Studio nem sobrescrever um arquivo anterior:

```bash
make prepare-tasks
```

O arquivo `data/treinamento/label_studio/tarefas.json` contém referências às
páginas, não suas imagens. O iniciador configura o serviço local de arquivos
com a raiz `data/treinamento/paginas/`.

O conversor GGUF usa o ambiente Python 3.12 separado `.venv-conversao/`,
com dependências fixadas em `requirements/conversao.txt`. O clone ignorado
`tools/llama.cpp/` está na revisão
`a8ad690ca9239ea35db4de47e00cf632d01895fd`; use essa revisão ao recriá-lo.
Para verificar a ajuda do conversor a partir da raiz do projeto:

```bash
make convert
```

O pipeline suporta treino Hugging Face no Linux com o modelo
[SmolVLM-256M-Instruct](https://huggingface.co/HuggingFaceTB/SmolVLM-256M-Instruct),
conversão GGUF, `mmproj` e execução por [llama.cpp](https://github.com/ggml-org/llama.cpp).
Os GGUF oficiais estão em
[ggml-org/SmolVLM GGUF](https://huggingface.co/collections/ggml-org/smolvlm-gguf).
Não ative um adaptador sem comparar
base e adaptado no conjunto `test` reservado e gerar uma aprovação positiva.

O fluxo completo de Codespaces, publicação autorizada e treino no GitHub está em
[pipeline de treinamento visual](docs/40_testing/05_pipeline_treinamento_visual.md).

## Documentação e código

- [Leia primeiro](01_leia_primeiro.md) e [índice da documentação](docs/70_documentation/01_index.md)
- [Status e limitações](docs/00_status_auditoria.md)
- [Organização do código e dos testes](docs/70_documentation/04_estrutura_projeto.md)
- [Changelog e política de versões](docs/60_project/04_changelog_projeto.md)
- [Arquitetura do agente](docs/50_architecture/02_ai_agent_architecture.md)
- [Casos propostos para memória e isolamento](docs/70_documentation/06_casos_teste_memory.md)
- [Contratos e dados JSON](json/README.md)
- [Aplicação Streamlit](src/health_refund_assistant/web/web_app.py)
- [Fluxo de extração, avaliação e resposta](src/health_refund_assistant/conversation/assistant.py)

O benchmark da extração fica fora do núcleo da aplicação:

```bash
make toolbox-help
make evaluate PROMPT=v4.2
```

Uma avaliação real usa a API configurada e gera um relatório local. O antigo
`scripts/case_evaluation_v3.py` gerava resultados fixos em sua implementação
histórica; seus relatórios anteriores não são evidência de testes reais. Os
comandos antigos de `scripts/` foram substituídos pelos da toolbox.
