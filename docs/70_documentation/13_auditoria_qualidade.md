# Auditoria de qualidade

## Objetivo

Verificar legibilidade, manutenção, duplicação, padrões de prompts e
comportamento do agente sem substituir as regras determinísticas.

## Organização

- Use `Makefile` para comandos comuns.
- Use `src/` para código Python.
- Use `tests/unit/` por domínio e `tests/integration/` para interfaces.
- Use `docs/` por categoria numerada.
- Use `prompts/` por componente e versão.
- Use `json/` por processo e schema.

## Agente

O projeto é um assistente controlado por estado, não um agente autônomo.

Estados:

- `aguardando_documento`
- `aguardando_exportacao`
- `aguardando_confirmacao`
- `analisando`
- `aguardando_revisao`
- `concluido`

O interpretador usa GPT-6 Luna para intenção. O Python registra ferramentas,
preserva estado e chama o fluxo determinístico. Quando o modelo textual não
estiver disponível, o fallback usa classificação local limitada.

## Prompts

Os prompts ativos devem conter:

1. `Tarefa`
2. `Entrada esperada`
3. `Saída esperada`
4. `Guardrails`

Não copie o schema JSON inteiro no prompt. O código fornece o schema pelo nome
e valida a resposta. Use uma nova versão ao alterar o contrato ou o comportamento.

## Qualidade do código

- Funções pequenas e com uma responsabilidade.
- Nome de função deve dizer o que ela faz.
- Imports não usados devem ser removidos.
- Dependências externas ficam em arquivos `requirements/`.
- Comandos operacionais ficam no `Makefile`.
- Dados pessoais e modelos locais ficam fora do Git.
- Evidências não validadas não são apresentadas como fatos.

## Pontos corrigidos

- Nova conversa limpa PDF, imagem e exportações pendentes.
- Adicionado registro explícito de tarefas/ferramentas no agente.
- Prompt do agente e outros prompts ativos padronizados.
- Guardrail de prazo removido da montagem dinâmica da resposta e mantido no
  prompt versionado.
- Comandos ativos da documentação substituídos por targets Make.
- Documentos históricos marcados como histórico.

## Pendências

- Validar modelo GGUF real no Codespaces.
- Aprovar adaptadores somente após teste reservado com ganho mensurável.
- Confirmar isolamento e autenticação antes de uso compartilhado.
