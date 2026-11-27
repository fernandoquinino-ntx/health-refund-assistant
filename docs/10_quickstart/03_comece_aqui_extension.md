# Extensão de navegador

A versão carregável única está em [`src/extension/`](../../src/extension/),
com [`manifest.json`](../../src/extension/manifest.json) na raiz. Consulte o
[guia de instalação e uso](../../src/extension/50_docs/09_guia_rapido.md) e o
[formato da exportação](../../src/extension/50_docs/10_exportacao_reembolsos.md).

Em Chrome ou Chromium, abra `chrome://extensions`, habilite o modo de
desenvolvedor e selecione a pasta `src/extension/` em **Carregar sem compactação**.
A coleta depende do portal e precisa ser validada no navegador; o arquivo
exportado pode conter dados de saúde.

O código é organizado em `10_popup/`, `20_background/`, `30_content/`,
`40_collector/`, `50_docs/` e `60_schemas/`. O comando `make build-extension` gera:

- `build/extension/`: pasta para carregar no Chrome em modo desenvolvedor;
- `build/care-plus-reembolsos-<versão>.zip`: pacote Chrome compatível para
  distribuição ou upload à Chrome Web Store;
- `.sha256`: checksum do ZIP.

Em cada tag `v*.*.*`, o workflow anexa ZIP e checksum à release no GitHub.
