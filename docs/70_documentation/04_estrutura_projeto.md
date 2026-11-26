# Estrutura do projeto

```text
src/health_refund_assistant/
├── core/          # caminhos, contratos JSON e biblioteca de prompts compartilhados
├── conversation/  # orquestração do assistente e memória individual
├── documents/     # PDF, processamento e extração VLM
├── plan/          # importação da extensão, avaliação e conciliação
└── web/           # interface Streamlit
src/anotacao_documentos/  # programa independente de preparação de labels
src/toolbox/       # ferramentas operacionais e avaliador
data/treinamento/  # PDFs, imagens e anotações privadas ignorados pelo Git
tests/
├── unit/          # testes unitários
└── integration/   # cenários sintéticos e interface
```

Os pacotes Python usam nomes descritivos em `snake_case`, sem prefixos numéricos:
isso permite imports comuns e execução com `python -m`.
Os módulos compartilhados ficam em `core/`; por exemplo,
`health_refund_assistant.core.json_contracts` e
`health_refund_assistant.core.paths`. Os antigos caminhos de importação desses
módulos não são mantidos.

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

`src/extension/` é a única fonte da extensão Chrome. `manifest.json` fica na
raiz dessa pasta e o código é organizado em categorias. O script
`make build-extension` gera uma cópia plana em
`build/extension/` sem duplicar o código fonte.

O programa [anotacao_documentos](../../src/anotacao_documentos/) prepara e
verifica anotações para um dataset visual. O pacote
[treinamento_visual](../../src/treinamento_visual/) monta, valida e treina
adaptadores LoRA visualmente. Instruções e limites estão no
[guia de anotação](../40_testing/04_anotacao_documentos.md) e na
[pipeline visual](../40_testing/05_pipeline_treinamento_visual.md).

## Avaliação e testes

O [case_evaluation.py](../../src/toolbox/case_evaluation.py) compara a saída
real do VLM com gabaritos sintéticos e grava um relatório local. O nome histórico
`scripts/case_evaluation_v3.py` foi removido; sua implementação mais antiga
gerava afirmações fixas, não resultados observados.

```bash
make test
make test-agent
make build-extension
```

O benchmark exige configuração e acesso ao modelo e pode gerar custos. Testes
automatizados com mocks não comprovam que a API ou o Codespaces funcionem.
Os caminhos e schemas de teste ficam em
[test_paths.py](../../src/toolbox/test_paths.py), fora do pacote da aplicação.
