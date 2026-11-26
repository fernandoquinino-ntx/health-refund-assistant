# Extensão de navegador

A versão carregável está em [`extension/`](../../extension/), com
[`manifest.json`](../../extension/manifest.json) na raiz. Consulte o
[guia de instalação e uso](../../extension/LEIAME.md) e o
[formato da exportação](../../extension/exportacao_reembolsos.md).

Em Chrome ou Chromium, abra `chrome://extensions`, habilite o modo de
desenvolvedor e selecione a pasta `extension/` em **Carregar sem compactação**.
A coleta depende do portal e precisa ser validada no navegador; o arquivo
exportado pode conter dados de saúde.

[`src/extension/`](../../src/extension/) é uma reorganização ainda não validada:
contém `01_manifest.json`, não o nome exigido pelo navegador, e não deve ser
usada como substituta antes de corrigir e testar os caminhos. Não remova nenhuma
das cópias sem validar a substituição.
