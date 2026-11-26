# Status do Codespaces

O [dev container](../../.devcontainer/devcontainer.json) declara Python,
instalação de dependências, geração de fixtures e encaminhamento da porta 8501.
A existência dessa configuração não comprova uma execução bem-sucedida.

Siga a [verificação manual](../40_testing/03_verificacao_codespaces_ui.md) e
registre resultados reais. Não compartilhe a porta para dados de saúde: a
aplicação não possui autenticação ou isolamento multiusuário.
