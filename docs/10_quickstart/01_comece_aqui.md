# Início rápido

Consulte o [README](../../README.md) para detalhes do fluxo e limitações.

## Preparar o ambiente

Na raiz do repositório, com Python 3.10 ou superior:

```bash
make setup
```

Configure `OPENAPI_TOKEN` no ambiente ou como segredo do Codespaces, sem
compartilhar seu valor. O projeto não carrega `.env` automaticamente.
`OPENAI_BASE_URL` é opcional; a disponibilidade do modelo padrão `gpt-6-luna`
depende do provedor configurado.

## Testar e iniciar

```bash
make test
make run
```

Abra a porta 8501. Converse com o agente e anexe os documentos quando ele solicitar.
Teste com dados sintéticos. Testes automatizados não comprovam a disponibilidade
da API nem uma execução real no Codespaces.

O [dev container](../../.devcontainer/devcontainer.json) configura dependências,
fixtures e encaminhamento da porta, mas a execução no Codespaces deve ser
verificada. Não compartilhe a porta: não há autenticação ou isolamento de usuários.
Use dados sintéticos.

Para a extensão de navegador, consulte o [guia da extensão](03_comece_aqui_extension.md).
