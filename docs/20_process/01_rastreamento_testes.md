# Rastreamento de testes

Para executar a suíte mantida pelo projeto, use:

```bash
make test
```

O [test_tracker.py](../../src/toolbox/test_tracker.py) é uma ferramenta opcional,
acessível com `.venv/bin/python -m toolbox rastrear`. O modo `run` usa a mesma
descoberta unittest da suíte principal e grava log e relatório locais; `--verbose`
mostra os nomes dos testes. O modo `test` aceita um nome completo unittest, e
`report` mostra o último relatório salvo. O processo retorna falha quando os
testes falham ou excedem o limite. A saída é mostrada após o subprocesso
terminar, não em tempo real; o relatório descreve uma execução, não cada teste.
Os arquivos em `json/evaluation/reports/` podem conter dados sensíveis e são
ignorados pelo Git. O rastreador não é necessário no CI.
