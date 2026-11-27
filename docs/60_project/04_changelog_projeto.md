# Changelog e versionamento

Registro de alterações relevantes do projeto. Consulte o histórico Git para os
detalhes de cada commit.

## Não lançado

### Versão declarada

- **0.4.5**: interface principal convertida para chat único. Importação de
  exportação e envio de PDF aparecem somente quando o agente solicita. Respostas
  neutras de encaminhamento foram movidas para `agente_conversacional/v1.1`;
  a classificação continua usando GPT-6 Luna com fallback determinístico.
  142 testes locais passaram.

- **0.4.4**: correção de reinício seguro no Codespaces. O startup agora encerra
  somente processos Streamlit desta aplicação na porta 8501 e inicia o código
  mais recente do checkout. Inclui `make restart`, execução automática no
  `postStartCommand` e teste de dispatch da ferramenta.

- **0.4.3**: a esteira de treinamento respeita o gate de consentimento sem
  bloquear o CI. Quando o consentimento está pendente, o workflow registra o
  motivo e pula treino, avaliação e conversão; dados privados só são processados
  após aprovação explícita.

- **0.4.2**: correções da esteira GitHub Actions e da toolbox. A operação
  `build_extension` recebe corretamente nenhum argumento quando chamada pelo
  CLI, o workflow de treino usa `PYTHONPATH=src` e foi adicionado teste de
  regressão para o dispatch. Todos os 139 testes locais passaram.

- **0.4.1**: autenticação local baseada em arquivo com usuário padrão de teste
  `Fernando Pimenta Quinino` e regras D-2/365 ativadas conforme a definição
  operacional acordada. D-2 exige D-2 dias em relação à importação e cobertura
  da exportação; 365 dias bloqueia novo pedido sem candidato localizado.
  O Codespaces instala Make, CMake e ferramentas de compilação antes do setup.

- **0.4.0**: implementação da evolução registrada nos insights do projeto.
  Inclui contrato central das tarefas, categoria não mapeada, autenticação local
  por usuário/PIN, memória e trilha JSONL por usuário, rastreamento na UI,
  regras D-2/365 opt-in, exportação/reimportação individual e testes sintéticos
  por grupo. Os recursos locais não substituem segurança de produção.

- **0.3.7**: consolidação do plano de evolução baseado nos insights do projeto.
  Os itens foram confirmados e transformados em critérios de implementação no
  plano `docs/60_project/05_plano_evolucao_insights.md`.

- **0.3.6**: correções finais de distribuição e observabilidade. O workflow de
  extensão passa a observar os caminhos Python atuais, o Label Studio usa
  telemetria somente por opt-in explícito e o repositório ganha validação
  automática de smoke da aplicação em ambiente Linux.

- **0.3.5**: auditoria final, Makefile sem duplicatas, scripts Shell removidos,
  prompts ativos validados e operação centralizada na toolbox Python.

- **0.3.4**: auditoria DRY/KISS concluída, prompts ativos estruturados,
  reset seguro de anexos pendentes, operações movidas para `src/toolbox/`,
  shell scripts operacionais removidos e Makefile como fluxo principal.

- **0.3.3**: auditoria documental e de prompts concluída; estado pendente
  isolado em nova conversa, prompts ativos padronizados e documentação operacional
  centralizada no Makefile.

- **0.3.2**: correções de auditoria; exportação pendente removida em nova
  conversa, prompts ativos padronizados com entrada/tarefa/saída/guardrails,
  registro básico de ferramentas do agente e comandos Makefile documentados
  nas guias operacionais.

- **0.3.1**: correções de consistência documental, Makefile principal,
  padronização dos prompts ativos, limpeza de estado pendente e registro
  explícito de ferramentas do agente.

- **0.3.0**: separação correta entre GPT-6 Luna para tarefas textuais e
  modelo SmolVLM GGUF para visão, runtime llama.cpp no Codespaces, avaliação
  reservada de adaptadores e ativação automática somente após aprovação.

- **0.2.0**: interface conversacional, estados de tarefa com interpretação
  estruturada GPT-6 Luna, anexos naturais, reorganização do repositório e
  pipelines de extensão/treinamento visual.

### Adicionado

- Contrato central em `json/config/agent_tasks.json`, tarefa
  `categoria_nao_mapeada`, autenticação local com PIN hash, memória por usuário,
  trilha JSONL privada e painel local de auditoria na interface.

- Exportação de análise individual em JSON e reimportação validada pelo
  assistente, além de regras D-2 e 365 ativáveis somente por configuração
  confirmada.

- Matriz sintética com cinco casos por grupo funcional e guardrails críticos
  para classificação desconhecida, prompt injection e acesso entre usuários.

- Plano de evolução consolidado em
  `docs/60_project/05_plano_evolucao_insights.md`, com confirmações do estado
  atual, fases de implementação, critérios de aceite, guardrails e matriz mínima
  de cinco casos por grupo.

- Workflow `containers.yml` para validar o JSON do devcontainer e iniciar a UI
  Streamlit em modo headless em um runner Linux durante pushes e pull requests.

- Configuração opcional de telemetria do Label Studio no `.env.example`, com
  ativação separada por `LABEL_STUDIO_TELEMETRIA=true` e DSNs explícitos.

- Dependências organizadas em `requirements/` por ambiente e `Makefile` com
  comandos para setup, testes, ingestão, labels, treino, conversão, extensão e limpeza.

- UI conversacional do assistente com estados da tarefa, anexos naturais,
  solicitação progressiva de documento/exportação e documentação dos casos de uso.

- Organização do repositório: scripts operacionais em
  `src/treinamento_visual/scripts/`, adaptadores em `models/adapters/` e testes
  por domínio em `tests/unit/10_application/`, `tests/unit/20_training/` e
  `tests/unit/30_toolbox/`.
- Extensão Chrome consolidada em `src/extension/`; `build_extension.sh` gera
  a cópia instalável sem manter uma segunda implementação na raiz.

- Pipeline Git para treino visual: workflow acionado por push, consentimento
  explícito de dados anonimizados, exportação segura do Codespaces e artefato
  de adaptador no GitHub Actions.
- Teste comparativo mostrou que os adaptadores curtos não devem ser ativados:
  o adaptador melhorado chegou a alucinar campos fictícios e repetir tokens
  visuais no documento reservado.

- Pipeline Git para treino visual: workflow acionado por push, consentimento
  explícito de dados anonimizados, exportação segura do Codespaces e artefato
  de adaptador no GitHub Actions.

- Pipeline de conversão do modelo visual para artefatos GGUF/mmproj, com
  ambiente separado, modelo leve SmolVLM, exportação LoRA MLX e execução
  automática ao iniciar um Codespace.
- Comutador `LOCAL_VLM_MODEL`/`LOCAL_VLM_ADAPTER` para avaliar modelos locais
  sem alterar o comportamento padrão da API remota.

- Configuração inicial de campos e transcrição por região e preparação de
  referências locais de tarefas para o Label Studio; isolamento de rede e
  integração de importação/exportação ainda pendentes.
- Ingestão local de PDFs e imagens JPG/PNG para treinamento visual: renderização
  dos PDFs a 300 DPI e OCR com palavras, caixas e linhas em área ignorada.
- Ambiente isolado e dependências fixadas para o conversor GGUF; a ajuda foi
  verificada, mas a conversão do modelo visual ainda não foi testada.
- Estrutura inicial do treinamento visual em `src/treinamento_visual/`, com
  pastas privadas para dados e modelos; as etapas ainda não estão implementadas.
- Preparação local de páginas de PDFs e conferência de anotações LabelMe para
  dataset visual, em `src/anotacao_documentos/`, com guia de privacidade,
  modelo sugerido e uso posterior em avaliação ou treino.
- Prompts versionados de extração `v4.2`, revisão `v1.1`, mapeamento `v1.2`
  e resposta `v1.2`; extração inclui trechos da IA para revisão humana.
- Prompts de extração `v4.1` e de mapeamento `v1.1`, sem duplicar o formato JSON.
- Instruções do Copilot para preservar a organização, os contratos e os padrões.
- Esta política de changelog e versionamento.

### Alterado

- O iniciador do Label Studio aceita telemetria apenas após opt-in; sem a
  configuração explícita, Sentry e analytics ficam desativados por padrão.

- O workflow da extensão Chrome passou a detectar mudanças na toolbox Python,
  sem referências aos scripts Shell removidos do treinamento visual.

- O vocabulário operacional passou a explicar que Sentry é externo e opcional,
  sem coletar dados privados por configuração automática.

- Label Studio isolado usa Sentry compatível; o iniciador local desativa Sentry
  e analytics, usa sandbox de rede do macOS e mantém o banco e os dados em
  `data/treinamento/`. O navegador ainda não está isolado.
- Registrada a versão do Tesseract verificada no Mac para o futuro fluxo de
  treinamento visual e a orientação de compatibilidade para o Codespace.
- Ferramentas operacionais migradas de `scripts/` para `src/toolbox/`; os comandos
  antigos foram substituídos. CI e execução local usam a mesma suíte unittest
  com fixtures versionadas, sem regenerá-las automaticamente.
- Rastreamento opcional usa unittest, retorna falhas e registra duração observada;
  logs de execução também são ignorados pelo Git.
- Cabeçalhos Python documentam objetivo, entradas, processamento e saídas.
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
  `0.4.5` em `pyproject.toml` e `src/health_refund_assistant/__init__.py`.
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
