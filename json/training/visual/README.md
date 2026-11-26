# Dataset visual aprovado

Este diretório contém somente dados anonimizados que podem ser usados pelo
GitHub Actions. Dados pessoais, PDFs reais e o banco do Label Studio devem
permanecer em `data/treinamento/`.

Estrutura:

- `consentimento_publicacao.json`: gate obrigatório; `aprovado` deve ser `true`.
- `dataset/train.jsonl`, `valid.jsonl`, `test.jsonl`: exemplos sem dados pessoais.
- `images/`: imagens anonimizadas referenciadas pelos JSONL.

O push inicia o treino somente depois de revisar o consentimento e os arquivos
incluídos no commit. O workflow publica o adaptador como artefato de Actions,
não faz commit automático de pesos no repositório.
