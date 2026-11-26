# Treinamento visual

Índice dos componentes:

- `ingest/`: OCR, renderização 300 DPI e manifestos privados.
- `label/`: configuração e iniciador isolado do Label Studio.
- `train/`: build do dataset, validação, exportação pública e treino.
- `scripts/`: inicialização do Codespace, conversão GGUF e build da extensão.
- `eval/`: pacote reservado para avaliação futura.

Fluxo privado:

1. Coloque PDFs/imagens em `data/treinamento/entrada/`.
2. Execute ingestão, OCR e prepare o Label Studio.
3. Revise visualmente todas as caixas.
4. Execute `build_dataset.py` e `check_dataset.py`.
5. Exporte dados anonimizados somente depois de revisão e consentimento.
6. Faça push; o workflow governa o treino Linux no GitHub Actions.

Consulte [a documentação do pipeline](../../docs/40_testing/05_pipeline_treinamento_visual.md).
## Atalho para leigos

Use `make help` para ver os comandos. O fluxo usual é:
`make ingest → make prepare-tasks → make label-studio → make build-dataset →
make check-dataset → make train-mac → make evaluate-adapter →
make approve-adapter → make convert`.

Não chame o adaptador de “modelo” completo. Ele é uma correção pequena aplicada
sobre o modelo base SmolVLM. Não publique nem ative sem avaliação reservada.
