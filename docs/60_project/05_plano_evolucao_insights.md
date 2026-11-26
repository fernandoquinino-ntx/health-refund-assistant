# Plano de evolução a partir dos insights do usuário

Atualizado em 26/11/2026.

## Objetivo

Fechar os comportamentos do assistente de modo simples e auditável, sem tratar
regras do plano como fatos antes da confirmação da Care Plus. Este plano separa
decisões confirmadas, lacunas já confirmadas no código e trabalhos futuros.

## Confirmações do estado atual

### Entrada de documento

O PDF mencionado é a nota fiscal ou o recibo. O sistema aceita:

- PDF editável ou escaneado;
- PDF convertido pela primeira página para imagem;
- JPG e PNG;
- exportação JSON do plano.

A implementação envia apenas a primeira página para a visão documental. Isso
não confirma processamento de páginas adicionais sem testes específicos.

### Proteção contra conteúdo malicioso

Os schemas JSON e os guardrails atuais reduzem alucinação e instrução indevida,
mas não garantem proteção contra prompt injection. A segurança depende de testes
explícitos, revisão humana e regras determinísticas em Python.

### Prazos

- 30 dias é uma regra **simulada**, configurável na interface.
- Cinco dias úteis é uma estimativa informada pelo usuário, não confirmada pela
  Care Plus e não considera feriados.
- D-2 e 365 dias aparecem em documentos históricos, mas não estão implementados
  no fluxo atual.
- A elegibilidade continua como “não é possível avaliar” sem regras verificadas.

## Lacunas confirmadas

| Insight | Situação atual | Correção planejada |
|---|---|---|
| README precisa explicar PDFs e saídas | PDF e tarefas estão descritos, mas exemplos e saídas por chat estão incompletos | Separar exemplos de nota PDF, imagem e exportação; mostrar entrada, resposta e evidências |
| Prazo de cinco dias precisa vínculo com Care Plus | Somente texto informativo existe | Configurar como estimativa provisória até confirmação contratual |
| Revisão consultiva precisa ser específica | Está genérica no README | Chamar de revisão da primeira página da nota por IA |
| Estimativa não expõe seu JSON | O schema existe em `json/plan/schemas/payment_estimate.schema.md` | Referenciar o schema e todos os campos no README e no guia da tarefa |
| Respostas possíveis não têm um catálogo fechado | Tarefas e enum existem no agente, mas não há registro único | Criar um contrato central de tarefas |
| “Novo PDF após conversa salva” não está explicado | Estado salvo não contém PDF | Explicar que memória salva texto/evidências, não o arquivo original |
| Porta 8501 não está explicada | README menciona a porta sem contexto | Explicar que é porta HTTP local da UI Streamlit |
| Codespaces não usa Make como entrada principal | Dev container chama a toolbox diretamente | Passar `make setup-codespace` no `postCreateCommand` |
| Leia primeiro e referência rápida parecem duplicados | Há sobreposição real | 01 guia sequencial; 02 apenas comandos e decisão rápida |
| D-2 não está explicado | O conceito aparece em arquitetura histórica | Definir regra somente após receber contrato confirmado |
| Sem autenticação nem isolamento | Confirmado no código e no status | Implementar MVP local com usuários e diretórios separados |
| Sem rastreamento completo da IA na UI | Existem relatórios de suíte, não trilhas por conversa | Criar JSONL de eventos e visão de auditoria |
| Usuário novo não identificado | Estado inicial não exige identidade | Perguntar e validar identidade antes de carregar memória |
| Casos por grupo são insuficientes | Existem cenários sintéticos, mas não cinco por intenção principal | Criar matriz de 5 casos por grupo |
| Importação/exportação não têm fluxo simétrico | Extensão exporta JSON e UI importa JSON | Definir exportação segura de resultado individual e lote |

## Contrato central do agente

Criar `json/config/agent_tasks.json` ou JSON equivalente, mantendo somente os
campos necessários:

```json
{
  "task": "verificar_prazo",
  "recognized_aliases": [],
  "minimum_inputs": ["documento", "data_referencia"],
  "missing_input": "documento",
  "prompt": "reembolso_assistente/v1.2",
  "schema": "json/documents/schemas/assistant_answer.schema.json",
  "deterministic_tools": ["avaliar_documento"],
  "allowed_outputs": ["dentro_do_prazo", "prazo_ultrapassado", "nao_e_possivel_avaliar"],
  "guardrails": []
}
```

Adicionar uma tarefa explícita `categoria_nao_mapeada` para entradas fora do
catálogo. Ela deve pedir esclarecimento ou mostrar opções sem inventar execução.
A intenção nunca deve cair silenciosamente em `analisar_documento`.

## Fases de implementação

### Fase 1: contratos e documentação

1. Consolidar o catálogo de tarefas, entradas mínimas, prompts, schemas e saídas.
2. Reescrever o README com exemplos reais sintéticos para:
   - nota PDF editável;
   - PDF escaneado;
   - JPG/PNG;
   - exportação JSON;
   - status, pagamento, prazo, completude e tarefa desconhecida.
3. Diferenciar “Leia primeiro” de “Quick Reference”.
4. Explicar porta 8501, memória local, nova análise com PDF e o significado de D-2.
5. Referenciar os JSONs padronizados da resposta do agente e da estimativa.

Aceite: o usuário consegue seguir do README ao Make sem ler três documentos.

### Fase 2: regras de prazo

1. Colocar cinco dias úteis como configuração provisória, identificada na resposta.
2. Reservar D-2 e 365 dias como configurações futuras desativadas por padrão.
3. Quando houver exportação até hoje, informar que não exclui novas informações
   futuras e não conclui pagamentos anteriores sem registro.
4. Não usar prazo confirmado até existir fonte aprovada da Care Plus.

Sugestão de texto:

> Esta é uma estimativa provisória de cinco dias úteis. Não considera feriados e
> não foi confirmada pela Care Plus. Hoje é a data de referência porque a
> exportação consultada foi atualizada até esta data; novas informações podem
> aparecer em uma exportação posterior.

Aceite: nenhuma resposta chama prazo provisório de garantia ou regra confirmada.

### Fase 3: autenticação e isolamento simples

Implementar primeiro um arquivo local de usuários e PINs hash, não CPF nem
credenciais reais no repositório. Os diretórios deverão ser separados por
`user_id`.

- Arquivo ignorado pelo Git;
- PIN armazenado com hash;
- sessão apenas depois da validação;
- nenhuma conversa pode carregar dados de outro usuário;
- “usuário não identificado” apresenta o login e não inicia análise;
- apagar conversa remove somente os dados daquele usuário;
- testes com usuários sintéticos Fernando e Maria.

Aceite: teste de acesso cruzado, path traversal e memória vazia para usuário novo.

### Fase 4: rastreabilidade da UI

Criar um evento JSON por interação:

- `event_id`, `timestamp`, `user_id`;
- `task` reconhecida e confiança;
- versões do agente, VLM, revisão e resposta;
- entrada sanitizada ou hash da entrada;
- anexos identificados por hash;
- schema usado e resultado da validação;
- saída sintética/resposta;
- duração, erros e status;
- resultado determinístico independente.

Armazenar em JSONL privado por usuário. Exibir uma tabela na UI com filtros por
versão, tarefa, status, prompt e data. Não registrar PIN, CPF ou conteúdo bruto
de PDFs sem consentimento.

Aceite: cada resposta abre a cadeia da conversa e permite comparar duas versões
de prompt com o mesmo conjunto de casos.

### Fase 5: importação e exportação

1. Validar JSON e período antes de anexar à sessão.
2. Permitir exportar o resultado de uma nota ou conversa individual.
3. Permitir reimportar um resultado sem revelar dados de outros usuários.
4. Mostrar exatamente quais dados serão exportados e exigir confirmação.
5. Bloquear exportação quando houver dados não revisados ou marcados privados.

Aceite: round-trip JSON e exportação segura passam em testes locais.

## Matriz mínima de testes

Para cada grupo principal, manter cinco casos positivos ou negativos:

| Grupo | Cinco casos mínimos |
|---|---|
| Identidade | Sem identidade, identidade conhecida, PIN correto, PIN errado, usuário desconhecido |
| Analisar documento | PDF editável, PDF escaneado, JPG/PNG, campo ausente, documento ilegível |
| Consultar status | Pedido localizado, pedido ausente, exportação parcial, registro conflitante, documento não localizado |
| Confirmar pagamento | Pago integral, pago parcial, recusado, sem status, status sem valor/data |
| Verificar prazo | Dentro do prazo, vencido, pedido localizado, data futura, exportação não cobre a data |
| Revisar completude | Dados completos, campo ausente, caixa ilegível, contradição visual/textual, instrução maliciosa |
| Tarefa não mapeada | Saudação, assunto fora de domínio, pedido ambíguo, tentativa de acesso, prompt injection |

Os conjuntos devem ser sintéticos e versionados. Os gabaritos não devem ser
enviados ao modelo como respostas esperadas.

## Guardrails prioritários

Testar pelo menos:

- instrução dentro do documento para revelar o prompt ou chave;
- pedido para confirmar pagamento sem evidência;
- pedido para alterar status por texto livre;
- tentativa de path traversal;
- tentativa de listar dados de outro usuário;
- JSON com chave extra ou campo ausente;
- duas exportações conflitantes;
- documento de hoje sem exportação atual;
- página ilegível ou sem campos;
- solicitação de resposta fora do domínio.

## Critérios de conclusão da próxima versão

- README revisado com exemplos por tipo de entrada e saída.
- Quick Reference separado do guia inicial.
- Contrato central de tarefas implementado e testado.
- Make usado no dev container.
- Identidade local simples e isolamento por usuário demonstrados.
- D-2/365 removidos da documentação ativa ou marcados como pendentes aprovados.
- Rastreio JSONL privado e tela de auditoria disponíveis.
- Exportação e reimportação validadas.
- Pelo menos cinco casos sintéticos por grupo principal.
- Nenhum teste usa dados reais de saúde.
