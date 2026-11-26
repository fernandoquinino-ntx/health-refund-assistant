# Anotação de documentos para extração visual

> Este guia combina o fluxo anterior com LabelEditor e o fluxo atual com
> Label Studio. O OCR é executado localmente e o dataset é validado antes do
> treino. Consulte também a [pipeline automatizada](05_pipeline_treinamento_visual.md).
> Não envie dados ao Codespace antes de anonimização, revisão e aprovação.

Este fluxo prepara **seus PDFs**, sem gerar dados de exemplo nem chamar um
modelo ou serviço externo. Serve para formar um conjunto de referência e,
posteriormente, convertê-lo para o formato exigido por um treinamento. Não
treina pesos, não avalia automaticamente a extração e não detecta fraude.

## Privacidade

PDFs, imagens, caixas, transcrições, nomes, hashes e exportações podem identificar
pessoas. `data/treinamento/` é ignorado pelo Git, mas isso não protege contra
acesso ao Codespace, compartilhamento, backups ou extensões. Use um Codespace
privado, porta privada e somente extensões confiáveis; não compartilhe arquivos
ou logs. Faça backup seguro e defina prazo de exclusão. Confira com `git status`
e `git check-ignore` antes de enviar código. Não use `git add -f`.

Sua autorização para envio se aplica aos dados **após anonimização**. Revise as
imagens, metadados, nomes e transcrições: cobrir nomes não garante anonimização.
Antes de enviar a um provedor, confira suas regras, retenção, acesso e requisitos
legais aplicáveis; se não puder garantir isso, mantenha-os em ambiente privado.
Treinamento, pesos e exemplos também podem reter ou revelar informações.

## Preparar imagens

No terminal do Codespace, instale as dependências conforme o README. Execute:

```bash
PYTHONPATH=src .venv/bin/python -m anotacao_documentos preparar
```

O comando cria `data/treinamento/entrada/` e `data/treinamento/paginas/`.
Coloque seus PDFs em `entrada/` e execute o mesmo comando novamente. Todas as
páginas são renderizadas em PNG, em um diretório por PDF. O identificador do
diretório é o SHA-256 do conteúdo: PDFs idênticos são tratados como um único
documento, mesmo com nomes diferentes; uma alteração cria outro identificador.
Guarde os PDFs originais para associar cada diretório ao documento correspondente.

Execuções repetidas preservam as páginas e anotações existentes. Para alterar a
renderização de um documento já preparado, faça backup seguro das anotações e
remova manualmente **somente o diretório desse documento** antes de repetir;
as caixas antigas não devem ser reutilizadas em imagens de dimensões alteradas.
PDFs protegidos por senha e arquivos inválidos são reportados como falhas.

## Marcar no LabelEditor

1. Verifique que `LabelEditor for VSCode` está disponível no ambiente remoto do
   Codespace. O funcionamento remoto ainda não foi verificado neste projeto.
2. No Explorer, abra uma imagem em `data/treinamento/paginas/doc_.../` com
   **LabelEditor: Open Image Annotator**.
3. Use retângulos ao redor do **valor impresso**, não do título; registre o
   rótulo e transcreva o texto visível no campo **Description**. Salve com
   Ctrl+S. O LabelEditor salva o JSON LabelMe ao lado da imagem.
4. Repita para todas as páginas. Se uma página revisada não tiver nenhum dos
   campos abaixo, registre-a com o comando a seguir, substituindo o caminho pela
   imagem correspondente. O comando não sobrescreve uma anotação existente.
   Ausência de JSON significa pendente.
```bash
PYTHONPATH=src .venv/bin/python -m anotacao_documentos sem_campos data/treinamento/paginas/doc_HASH/pagina_0001.png
```

5. Execute:

```bash
PYTHONPATH=src .venv/bin/python -m anotacao_documentos verificar
```

O verificador confere a quantidade de páginas renderizadas, exige um JSON por
página e confere dimensões, retângulos, rótulos e
transcrições não vazias, sem imprimir os valores. Ele não comprova se as caixas
ou transcrições estão corretas. Revise-as visualmente. JSONs lado a lado com as
imagens são uma exceção aos JSONs de aplicação em `json/`, necessária ao plugin.

| Rótulo | Texto a marcar |
|---|---|
| `numero_documento` | Número fiscal do documento |
| `prestador` | Nome do emissor |
| `cnpj_cpf_prestador` | Identificador fiscal do emissor |
| `valor_total` | Valor final impresso, não outro valor ou total calculado |
| `data_emissao` | Data identificada como emissão |
| `data_atendimento` | Data identificada como atendimento |
| `nome_profissional` | Nome do profissional responsável |
| `descricao_servico` | Descrição visível do serviço |
| `registro_profissional` | Conselho, número e UF visíveis |

Marque apenas o que estiver visível e legível. Não adivinhe campos ausentes.
Registre cada trecho em uma caixa; quando houver vários trechos do mesmo campo,
use o mesmo rótulo e transcreva cada um. O verificador não escolhe entre valores
ambíguos. Preserve o texto literalmente; a normalização para números, datas e
campos ausentes deverá ser definida e revisada na conversão futura.

## Modelo sugerido e etapas de treinamento

Para experimentar com visão, comece pelo
[Qwen2.5-VL-7B-Instruct](https://huggingface.co/Qwen/Qwen2.5-VL-7B-Instruct),
da mesma família do modelo que você já usa no LM Studio. A documentação do
modelo inclui leitura estruturada de documentos e localização visual, mas isso
não garante precisão nas suas notas. Caso a GPU seja insuficiente, experimente o
[Qwen2.5-VL-3B-Instruct](https://huggingface.co/Qwen/Qwen2.5-VL-3B-Instruct);
seu adaptador será para o 3B, não para o 7B.

1. Use o Codespaces para preparar, anotar e revisar os dados como descrito acima.
2. Separe treino, validação e teste por **documento**; mantenha documentos muito
   semelhantes ou da mesma origem no mesmo conjunto quando possível.
3. Crie para cada exemplo uma imagem, uma instrução e uma **resposta completa
   revisada** com os campos desejados. Caixas e transcrições do LabelEditor não
   são automaticamente exemplos completos de ajuste fino supervisionado.
4. Após conferir a anonimização e as condições do serviço, use uma máquina com
   GPU, como um runtime do Colab, e converta os exemplos para o formato da
   [ferramenta de treinamento Qwen VL](https://github.com/QwenLM/Qwen3-VL/tree/main/qwen-vl-finetune).
   Considere LoRA para ajustar um adaptador em vez de todos os pesos. GPU, memória,
   tempo e preço variam; não há garantia de que o 7B caiba no Colab disponível.
5. Avalie o modelo original e o ajustado no mesmo conjunto de teste nunca visto,
   comparando campos e erros. Um resultado melhor não é garantido.
6. Para testar no LM Studio, confira como exportar a combinação de modelo,
   adaptador e componente visual para um formato compatível com sua versão.
   Essa conversão e execução precisam ser testadas com o treinamento escolhido.

O projeto monta conjuntos privados, valida campos contra OCR e oferece treino
LoRA por MLX no Mac. O Codespace atual não deve ser tratado como GPU de
treinamento. O GitHub Actions oferece uma alternativa Linux com
[pipeline automatizada](05_pipeline_treinamento_visual.md). Veja a
[FAQ do Colab](https://research.google.com/colaboratory/faq.html)
para limites e disponibilidade.

## Usar o ChatGPT público

Não é possível carregar o adaptador ou os pesos do Qwen no ChatGPT público para
substituir os pesos do modelo da OpenAI. Para aproveitar seu trabalho **sem
treinar o ChatGPT**:

1. Use os erros encontrados na avaliação para melhorar suas instruções de
   extração; compare versões usando o mesmo conjunto de teste.
2. Execute o Qwen treinado separadamente e envie ao ChatGPT somente o resultado
   anonimizado que desejar analisar. Isso usa a extração do Qwen, mas não altera
   os pesos do ChatGPT. Hoje o projeto ainda não automatiza essa passagem.
3. Alternativamente, um projeto no ChatGPT pode reunir instruções e arquivos de
   referência anonimizados. Esses arquivos são material de consulta, não pesos
   treinados. JSON LabelMe com coordenadas não se torna automaticamente
   aprendizado ou gabarito interpretado. Se usar exemplos de documentos, reserve
   outros documentos para teste.
4. Antes de enviar imagens ou exemplos, revise anonimização, consentimento e
   [controles de dados do ChatGPT](https://help.openai.com/en/articles/7730893-data-controls-in-chatgpt).
   Desativar uso para melhoria do modelo não equivale a apagar o histórico.
   A disponibilidade dos recursos e os termos dependem da conta e podem mudar.

A [OpenAI informa](https://help.openai.com/en/articles/8554397-creating-and-editing-gpts)
que contas pessoais não podem criar novos GPTs personalizados e que a função
está em transição para plugins. Uma futura integração via
[plugin](https://help.openai.com/en/articles/20001256) pode conectar ferramentas,
mas depende de disponibilidade, configuração e testes; não está implementada.

Na API da OpenAI, não há um passo para carregar o adaptador do Qwen como modelo
da OpenAI. A [documentação de fine-tuning visual](https://developers.openai.com/api/docs/guides/vision-fine-tuning)
informa que a plataforma está sendo encerrada e não aceita novos usuários;
confira a disponibilidade atual antes de planejar um ajuste fino nela.

## Acessar o LM Studio do Codespace (opcional)

O LM Studio está no seu computador, enquanto o Codespace roda em outra máquina:
`localhost` em um não é o `localhost` do outro. O servidor LM Studio oferece uma
[API compatível com OpenAI](https://lmstudio.ai/docs/developer/openai-compat),
mas isso **não é** a API nem o ChatGPT da OpenAI.

Uma opção a testar é um túnel SSH reverso privado:

1. No seu computador, inicie o servidor local do LM Studio na porta 1234, restrito
   a `127.0.0.1`. Mantenha autenticação ativada quando disponível.
2. No terminal do seu computador, com `gh` autenticado, substitua `NOME_CODESPACE`
   pelo nome real e mantenha o processo aberto:

   ```bash
   gh codespace ssh -c NOME_CODESPACE -- -N -o ExitOnForwardFailure=yes -R 127.0.0.1:1234:127.0.0.1:1234
   ```

3. Em outro terminal, dentro do Codespace, consulte apenas a lista de modelos:

   ```bash
   curl --fail http://127.0.0.1:1234/v1/models
   ```

   Se o servidor exigir autenticação, inclua o token conforme a documentação do
   LM Studio, sem registrá-lo em arquivos ou comandos compartilhados.
4. Encerrar o comando SSH fecha o túnel. Ele exige SSH disponível no Codespace
   e que a porta remota esteja livre. Esta conexão ainda não foi testada aqui;
   se falhar, não torne a porta pública para contornar o problema.

O assistente atual fixa o identificador `gpt-6-luna` em várias tarefas e usa
recursos de saída estruturada que precisam ser compatíveis. Alterar apenas
`OPENAI_BASE_URL` não garante que o aplicativo funcione com o Qwen no LM Studio.
Testar o túnel não envia PDFs; enviar imagens depois exige verificar o destino e
a privacidade.

Caixas e extração correta não comprovam autenticidade:
para isso, confira a fonte oficial ou a assinatura/XML quando disponíveis.

Referências: [Qwen2.5-VL](https://github.com/QwenLM/Qwen2.5-VL),
[Colab FAQ](https://research.google.com/colaboratory/faq.html),
[LM Studio](https://lmstudio.ai/docs) e
[LabelEditor](https://marketplace.visualstudio.com/items?itemName=ciuzaak.labeleditor-vscode).
