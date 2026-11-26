# Estrutura do projeto

```text
src/health_refund_assistant/
├── conversation/  # orquestração do assistente e memória individual
├── documents/     # PDF, processamento e extração VLM
├── plan/          # importação da extensão, avaliação e conciliação
├── web/           # interface Streamlit
├── json_contracts.py
└── paths.py
scripts/           # avaliação real, geração de fixtures e rastreamento
tests/
├── unit/          # testes unitários
└── integration/   # cenários sintéticos e interface
```

Os pacotes Python usam nomes descritivos em `snake_case`, sem prefixos numéricos:
isso permite imports comuns e execução com `python -m`.

## Fluxo principal

O [app.py](../../app.py) inicia a interface
[web_app.py](../../src/health_refund_assistant/web/web_app.py). Ela recebe a
pergunta, o PDF e o JSON exportado pela extensão do navegador. O
[assistant.py](../../src/health_refund_assistant/conversation/assistant.py)
coordena o [extrator](../../src/health_refund_assistant/documents/vlm_extractor.py),
a [avaliação](../../src/health_refund_assistant/plan/assessment.py), a
[conciliação](../../src/health_refund_assistant/plan/reconciliation.py) e a
resposta da IA. A importação do JSON é feita por
[plan_exports.py](../../src/health_refund_assistant/plan/plan_exports.py).

`extension/` contém a extensão carregável; `src/extension/` é uma reorganização
adicional cuja instalação ainda precisa ser verificada. O Chrome exige o nome
`manifest.json` na raiz da pasta carregada.

## Avaliação e testes

O [case_evaluation.py](../../scripts/case_evaluation.py) compara a saída real
do VLM com gabaritos sintéticos e grava um relatório local. O nome histórico
`case_evaluation_v3.py` chama esse mesmo avaliador; sua implementação anterior
gerava afirmações fixas, não resultados observados.

```bash
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python scripts/case_evaluation.py --help
```

O benchmark exige configuração e acesso ao modelo e pode gerar custos. Testes
automatizados com mocks não comprovam que a API ou o Codespaces funcionem.
Os caminhos e schemas de teste ficam em
[test_paths.py](../../scripts/test_paths.py), fora do pacote da aplicação.
