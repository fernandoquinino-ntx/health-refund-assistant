# Changelog e versionamento

Registro de alterações relevantes do projeto. Consulte o histórico Git para os
detalhes de cada commit.

## Não lançado

### Adicionado

- Prompts versionados de extração `v4.2`, revisão `v1.1`, mapeamento `v1.2`
  e resposta `v1.2`; extração inclui trechos da IA para revisão humana.
- Prompts de extração `v4.1` e de mapeamento `v1.1`, sem duplicar o formato JSON.
- Instruções do Copilot para preservar a organização, os contratos e os padrões.
- Esta política de changelog e versionamento.

### Alterado

- A interface seleciona as novas versões de extração, revisão e resposta, e o
  comando de mapeamento usa `v1.2` por padrão; contratos e prompts anteriores
  permanecem disponíveis. A IA continua a
  calcular a estimativa de pagamento, conferida de forma independente em Python.
- Guias de entrada, navegação e operação revisados; documentação histórica e
  propostas identificadas, com links JSON e limitações corrigidos.
- As tarefas de revisão, resposta e estimativa recebem, pelo código, o prompt,
  o schema JSON e um modelo gerado a partir do contrato.
- Módulos compartilhados de caminhos, contratos e prompts foram organizados em
  `src/health_refund_assistant/core/`; imports, documentação e testes foram atualizados.

### Compatibilidade

- Imports antigos `health_refund_assistant.paths`,
  `health_refund_assistant.json_contracts` e
  `health_refund_assistant.prompt_library` devem ser atualizados para os módulos
  correspondentes em `health_refund_assistant.core`.

## Histórico anterior

O commit `1695929` registra a reorganização do assistente, a estimativa de
processamento, os testes e a documentação. O histórico anterior está no Git;
não há release ou tag de versão registrada neste changelog.

## Política de versões

- A aplicação usa `MAJOR.MINOR.PATCH` (SemVer). A versão atualmente declarada é
  `0.1.0` em `pyproject.toml` e `src/health_refund_assistant/__init__.py`.
- Antes de `1.0.0`, `0.MINOR.0` pode incluir alterações incompatíveis ou novas
  funcionalidades; `0.MINOR.PATCH` registra correções compatíveis.
- A partir de `1.0.0`, incremente `MAJOR` para quebra de compatibilidade, `MINOR`
  para funcionalidade compatível e `PATCH` para correção compatível.
- Registre mudanças em **Não lançado** durante o desenvolvimento. Ao preparar
  uma release, escolha a versão conforme o impacto, atualize as duas declarações,
  mova as notas para uma seção com versão e data reais, valide e crie uma tag
  `vMAJOR.MINOR.PATCH`. Um commit ou push isolado não cria uma release.
- A extensão Chrome, os prompts e os schemas têm versões próprias; não os
  incremente automaticamente junto com a versão da aplicação.
