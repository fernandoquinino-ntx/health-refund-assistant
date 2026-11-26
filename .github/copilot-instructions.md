# Instruções do repositório

Leia [agents.md](../agents.md) e mantenha-o alinhado com este arquivo quando o
usuário alterar padrões do projeto.

- Use `snake_case`; documentos em `docs/` usam categorias e ordinais. Preserve
  os nomes exigidos por ferramentas, como `README.md` e `manifest.json`.
- Em `src/health_refund_assistant/`, coloque infraestrutura compartilhada em
  `core/` e funcionalidades em `conversation/`, `documents/`, `plan/` ou `web/`.
  O programa de anotação fica em `src/anotacao_documentos/` e seus dados
  privados em `data/treinamento/`. Mantenha testes em `tests/` e ferramentas
  operacionais independentes em `src/toolbox/`.
- Inicie cada arquivo Python com docstring de objetivo, entradas, processamento
  e saídas; nos demais arquivos de código, descreva sua função e etapa na forma
  apropriada da linguagem.
- Mantenha JSONs por processo em `json/`, caminhos em `core/paths.py` e prompts
  versionados em `prompts/`. O Python inclui o schema e o modelo JSON na tarefa
  de IA e confere a resposta; preserve versões históricas dos prompts.
- Atualize documentação, índices e imports afetados. Não invente resultados de
  testes nem afirme disponibilidade da API, do modelo ou do Codespaces sem testar.
- Diferencie instruções atuais de propostas e relatórios históricos; preserve
  modelos e resultados históricos sem tratá-los como verificação atual.
- Registre alterações relevantes em `docs/60_project/04_changelog_projeto.md`;
  siga sua política SemVer e não crie releases ou tags fictícias.
- Use somente dados sintéticos nos testes e não versione segredos ou dados de saúde.
- Use o Makefile como interface principal. Prompts ativos devem conter
  `Tarefa`, `Entrada esperada`, `Saída esperada` e `Guardrails`; não deixe
  instruções de IA fixas no Python. Operações novas vão para `src/toolbox/`,
  não para scripts Shell. Dependências da aplicação ficam no `pyproject.toml`;
  requisitos adicionais ficam em `requirements/`.
- Rode os testes relevantes; a suíte existente é
  `.venv/bin/python -m unittest discover -s tests -v`.
