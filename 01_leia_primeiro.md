# Leia primeiro

Este é um ponto de entrada para o projeto. O [README](README.md) é a referência
principal para instalação, funcionamento, privacidade e limitações.

## Comece por aqui

1. Leia o [README](README.md) e o [status atual](docs/00_status_auditoria.md).
2. Para preparar o ambiente, siga o [início rápido](docs/10_quickstart/01_comece_aqui.md).
3. Para encontrar outros assuntos, consulte o [índice](docs/70_documentation/01_index.md).
4. Para contribuir, leia as [instruções do projeto](agents.md) e o
   [changelog](docs/60_project/04_changelog_projeto.md).

## O que o assistente faz

A aplicação recebe uma pergunta, um PDF e uma exportação do plano. Extrai dados
com IA, confere estruturas e evidências, e apresenta uma resposta consultiva.
Apenas a primeira página do PDF é processada. Resultados devem ser conferidos
por uma pessoa; a aplicação não envia solicitações de reembolso.

Há uma estimativa de processamento de cinco dias úteis somente quando as
condições descritas no README são atendidas. A regra foi informada pelo usuário,
não foi confirmada com o plano e não considera feriados.

## Privacidade e validação

A memória é local, para um usuário, sem autenticação, isolamento multiusuário ou
criptografia. Não exponha a aplicação ou a porta do Codespace para dados de saúde.
Use dados sintéticos nos testes. Disponibilidade da API, do modelo, da extensão e
funcionamento no Codespaces precisam ser verificados no ambiente de uso.

O histórico de propostas, checklists e relatórios não comprova implementação,
resultado de testes ou prontidão para entrega.
