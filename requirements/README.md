# Dependências por ambiente

- `base.txt`: aplicação, Streamlit e contratos do assistente.
- `treinamento.in`/`treinamento.txt`: OCR e treino visual MLX no Mac.
- `conversao.in`/`conversao.txt`: conversão Hugging Face para GGUF.
- `label-studio.in`/`label-studio.txt`: interface local de rotulagem.
- `treinamento-ci.txt`: treino Linux no GitHub Actions.

Use o Makefile para criar os ambientes e instalar os arquivos. Não mantenha
dependências duplicadas na raiz do projeto.
