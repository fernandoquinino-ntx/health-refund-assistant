# Verificação manual no Codespaces

O [dev container](../../.devcontainer/devcontainer.json) prepara o ambiente e
encaminha a porta 8501. Isso não comprova que o Codespace, a API ou a interface
tenham sido testados.

1. Crie um Codespace do repositório e aguarde a configuração.
2. Configure `OPENAPI_TOKEN` como segredo do Codespaces. Não registre o valor.
3. Execute `make test`.
4. Inicie `make run` e abra a porta 8501.
5. Com dados sintéticos, importe uma exportação com período válido, anexe um PDF e
   faça uma pergunta. Confira os dados extraídos, as evidências e a resposta.
6. Registre somente resultados observados, incluindo erros e versões usadas.

O modelo exige acesso pela API e pode gerar custos. A aplicação não possui
autenticação ou isolamento multiusuário: não compartilhe a porta para dados de
saúde. Consulte o [README](../../README.md) e o
[roteiro de avaliação](../70_documentation/08_roteiro_avaliacao.md).
