# PDFs sintéticos

Esta pasta contém somente os PDFs fictícios C01–C15. Os templates e JSONs de avaliação
estão centralizados em `json/tests/`; consulte
[`json/README.md`](../../json/README.md). Recrie os documentos e fixtures com:

```bash
.venv/bin/python -m scripts.gerar_fixtures_sinteticas
```

Os PDFs ficam em `documentos/`. O manifesto, o gabarito e a exportação fictícia ficam
em `json/tests/synthetic/`. Nunca coloque documentos reais nesta pasta.
