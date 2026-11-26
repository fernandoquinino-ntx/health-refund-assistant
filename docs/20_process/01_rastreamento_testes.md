# Rastreamento de testes

Para executar a suíte mantida pelo projeto, use:

```bash
.venv/bin/python -m unittest discover -s tests -v
```

O [test_tracker.py](../../scripts/test_tracker.py) é uma ferramenta separada.
Ela invoca `python -m pytest` e, no modo `run`, requer também o plugin
`pytest-json-report`. Essas dependências não estão declaradas para instalação
padrão; seu funcionamento no Codespaces não foi verificado.

O resumo próprio do rastreador conta execuções registradas, não testes
individuais. Ele captura a saída após o subprocesso terminar, não em tempo real;
o modo `report` cria um relatório da instância atual, sem ler execuções
anteriores. Falhas e timeouts devem ser conferidos no log e no relatório: o
status de saída do script não é uma confirmação confiável de sucesso.
Os arquivos locais em `json/evaluation/reports/` podem conter dados sensíveis.
