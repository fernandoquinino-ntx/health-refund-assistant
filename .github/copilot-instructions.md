# Instruções do repositório

Leia [agents.md](../agents.md) e mantenha-o alinhado com este arquivo quando o
usuário alterar padrões do projeto.

- Use `snake_case`; documentos em `docs/` usam categorias e ordinais. Preserve
  os nomes exigidos por ferramentas, como `README.md` e `manifest.json`.
- Em `src/health_refund_assistant/`, coloque infraestrutura compartilhada em
  `core/` e funcionalidades em `conversation/`, `documents/`, `plan/` ou `web/`.
  Mantenha testes em `tests/` e avaliação em `scripts/`.
- Inicie cada arquivo de código com uma descrição breve da função e da etapa do
  processo, usando a forma apropriada da linguagem.
- Mantenha JSONs por processo em `json/`, caminhos em `core/paths.py` e prompts
  versionados em `prompts/`. O Python inclui o schema e o modelo JSON na tarefa
  de IA e confere a resposta; preserve versões históricas dos prompts.
- Atualize documentação, índices e imports afetados. Não invente resultados de
  testes nem afirme disponibilidade da API, do modelo ou do Codespaces sem testar.
- Registre alterações relevantes em `docs/60_project/04_changelog_projeto.md`;
  siga sua política SemVer e não crie releases ou tags fictícias.
- Use somente dados sintéticos nos testes e não versione segredos ou dados de saúde.
- Rode os testes relevantes; a suíte existente é
  `.venv/bin/python -m unittest discover -s tests -v`.
