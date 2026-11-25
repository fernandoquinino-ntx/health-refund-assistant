# Health Refund Assistant — Rastreabilidade Inteligente de Reembolsos Médicos

**Sistema de conciliação e auditoria determinística + assistente LLM para validar notas fiscais e status de reembolso em planos de saúde.**

---

## 📋 Visão Geral

O **Health Refund Assistant** resolve um problema real de rastreabilidade: beneficiários enviam notas fiscais e recibos médicos por e-mail ou WhatsApp para uma concierge que registra os pedidos manualmente no portal do plano de saúde. Como os comprovantes ficam dispersos em pastas ou conversas e as atualizações no portal ocorrem de forma assíncrona (às vezes levando semanas), perde-se a rastreabilidade.

O sistema:
1. **Extrai dados fiscais** de PDFs e imagens usando Vision Language Model (VLM) com schema JSON rigoroso.
2. **Valida contra exportação** do plano de saúde (exportada para JSON após ingestion).
3. **Responde 3 perguntas-chave** com fatos, não especulações:
   - **Rastreabilidade**: "Esta nota já foi submetida ao plano?"
   - **Status Financeiro**: "O reembolso foi pago, pago parcial/glosado, ou recusado?"
   - **Prontidão Pré-Envio**: "Esta nota está completa e dentro do prazo para submissão?"

---

## 🎯 Problema Real e Regras de Elegibilidade

### Contexto: Fluxo Manual Desordenado
- Beneficiário envia nota fiscal (PDF/imagem) por WhatsApp/e-mail.
- Concierge registra pedido manualmente no portal do plano (delay de dias/semanas).
- Beneficiário quer saber: foi submetida? Qual é o status? Pode enviar agora?
- **Problema**: Faltam dados estruturados, rastreabilidade é manual.

### Regra D-1 / D-2 (Corte Temporal e Elegibilidade)
O plano de saúde exporta periodicamente (geralmente diariamente) uma base de dados com pedidos processados até o corte **D-1** (dia anterior).

Dentro do sistema, aplicamos uma **janela de elegibilidade em D-2** como margem de segurança:
- **D-1**: Corte da exportação do plano (últimos pedidos processados).
- **D-2**: Janela de elegibilidade interna (D-1 menos 1 dia).
- **Notas com `data_emissao > D-2`**: Recebem status `FORA_DA_JANELA_IMPORTACAO` (não podem ser rastreadas na base importada; recomenda-se aguardar próxima exportação).

**Justificativa**: Evita falsos negativos quando uma nota é emitida após o corte D-1, impossibilitando que apareça na exportação. A janela D-2 garante que verificamos apenas notas que *poderiam* estar na base.

### Dois Modos de Operação

#### **Modo 1: Conciliação Financeira e Operacional** (Nota ≤ D-2)
Quando uma nota é submetida e sua `data_emissao` está dentro da janela (≤ D-2), o sistema:
1. Busca correspondência na exportação do plano.
2. Se **encontrada**: Retorna o status financeiro real:
   - `PAGO`: Reembolso pago integralmente.
   - `PAGO_PARCIAL`: Reembolso pago com glosa/devolução (calcula diferença).
   - `RECUSADO`: Pedido recusado pelo plano.
   - `EM_ANALISE`: Pedido ainda sob análise.
3. Se **não encontrada**: Passa para Auditoria Pré-Envio (veja Modo 2).

#### **Modo 2: Auditoria Pré-Envio** (Nota ≤ D-2 ou > D-2)
Quando uma nota não está na exportação (ou foi emitida fora da janela), o sistema valida se a nota está pronta para ser submetida:
1. **Completude Documental**: Verifica se contém todos os campos obrigatórios:
   - `CRM` ou `CRN` (profissional de saúde).
   - `descricao_servico` (descrição legível do serviço).
   - `cnpj_cpf_prestador` (CNPJ/CPF da clínica/profissional).
   - `data_emissao` (data de emissão da nota).
   - `valor_total` (valor cobrado).
2. **Prazo de Elegibilidade**: Verifica se a nota foi emitida dentro de **365 dias (1 ano)** — prazo limite do plano para submissão de pedidos de reembolso.
3. **Ressalva**: Ausência na exportação não prova isoladamente que o pedido nunca foi aberto (pode estar em processamento, perdido na fila, ou realmente não enviado). A auditoria só confirma que a *documentação* está pronta.

---

## 🏗️ Arquitetura do Fluxo

```
┌─────────────────────────────────────────────────────────────────────┐
│                     FLUXO DE PROCESSAMENTO                           │
└─────────────────────────────────────────────────────────────────────┘

                        PDF / Imagem
                             │
                             ▼
        ┌────────────────────────────────────┐
        │  VLM Extractor (gpt-4o-mini)       │
        │  Schema JSON com validação estrita │
        │  (CRM, descrição, valor, data)     │
        └────────────────────────────────────┘
                             │
                             ▼
        ┌────────────────────────────────────┐
        │  Conciliador & Auditor Determinístico │
        │  - Calcula D-2 (hoje - 2 dias)    │
        │  - Busca na Exportação do Plano   │
        │  - Valida 365 dias e campos       │
        └────────────────────────────────────┘
                             │
                 ┌───────────┴───────────┐
                 ▼                       ▼
        ┌──────────────────┐    ┌──────────────────┐
        │ Encontrado       │    │ Não Encontrado   │
        │ Modo 1:          │    │ Modo 2:          │
        │ Retorna Status   │    │ Auditoria        │
        │ (PAGO, RECUSADO, │    │ Pré-Envio        │
        │  EM_ANALISE)     │    │ (Completo? 365d?)│
        └──────────────────┘    └──────────────────┘
                 │                       │
                 └───────────┬───────────┘
                             ▼
        ┌────────────────────────────────────┐
        │  Assistente LLM (Chat)             │
        │  Síntese fundamentada na resposta  │
        │  (Fatos, sem invenção de status)   │
        └────────────────────────────────────┘
                             │
                             ▼
                     Resposta ao Usuário
                     (Rastreabilidade comprovada)
```

---

## 🚀 Guia de Execução

### Pré-requisitos
- **Python 3.9+**
- **Variáveis de Ambiente** (`OPENAI_API_KEY` obrigatório; os demais opcionais):
  ```bash
  OPENAI_API_KEY=sk-...  # Sua chave OpenAI
  OPENAI_BASE_URL=https://api.openai.com/v1  # (padrão)
  VLM_MODEL_NAME=gpt-4o-mini  # (padrão)
  LM_STUDIO_PORT=1234  # Se usar LM Studio localmente
  ```

### Configuração Rápida (GitHub Codespaces)
1. **Clone e abra no Codespaces**:
   ```bash
   git clone https://github.com/fernandoquinino-ntx/health-refund-assistant.git
   cd health-refund-assistant
   ```

2. **Adicione a API key em Codespaces Secrets**:
   - Vá para **Settings > Secrets and variables > Codespaces**.
   - Crie `OPENAI_API_KEY` com sua chave.

3. **Instale dependências**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Gere fixtures sintéticas** (PDFs de teste):
   ```bash
   python scripts/gerar_fixtures_sinteticas.py
   ```

5. **Execute o assistente interativo**:
   ```bash
   python src/assistant.py
   ```

6. **Ou execute a web app**:
   ```bash
   python src/web_app.py
   # Acesse http://localhost:8000
   ```

### Configuração Local (Máquina)
1. **Clone o repositório**:
   ```bash
   git clone https://github.com/fernandoquinino-ntx/health-refund-assistant.git
   cd health-refund-assistant
   ```

2. **Crie um `.env` com suas credenciais**:
   ```bash
   cp .env.example .env
   # Edite .env e adicione sua OPENAI_API_KEY
   ```

3. **Crie um ambiente virtual**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # macOS/Linux
   # ou
   venv\Scripts\activate  # Windows
   ```

4. **Instale dependências**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Execute os mesmos comandos acima** (assistente, web app, fixtures, testes).

### Executar Testes
```bash
# Todos os testes unitários
pytest -v

# Apenas testes de reconciliação
pytest tests/test_reconciliation.py -v

# Com cobertura
pytest --cov=src tests/
```

### Avaliação com Versões de Prompts (se API key disponível)
```bash
python scripts/case_evaluation.py --models v1.0 v2.0 v3.0
# Gera relatórios em json/evaluation/reports/
```

---

## 🔒 Segurança, LGPD e Limitações Conhecidas

### LGPD Compliance (Lei Geral de Proteção de Dados)
- ✅ **Repositório Git contém apenas dados sintéticos**: 15 PDFs fictícios em `data/sinteticos/documentos/` com nomes, CPFs e valores de teste.
- ✅ **Arquivos locais protegidos**: `.env` (credenciais) não é versionado; `.env.example` fornece template.
- ✅ **Sem dados pessoais no Git**: Exportações reais do plano, notas fiscais reais e dados de beneficiários **nunca** são commitados.
- ✅ **Limpeza**: Pasta `data/processed/` não contém PDFs reais; `json/documents/state/notas_extraidas.json` foi limpo para estrutura vazia válida.

### Segurança Contra Prompt Injection
- **Validação de entrada (VLM + Schema JSON)**: O VLM extrai dados com schema JSON `strict` mode (OpenAI); campos como `descricao_servico` são restringidos a tipos de dados (string, não código).
- **Teste adversarial (C14, C15)**: Casos de teste verificam defesa contra tentativas de Prompt Injection na descrição do serviço. Esperado: **zero falhas críticas** (a descrição não consegue quebrar a lógica de conciliação).
- **Tokens & Lógica**: A conciliação é **determinística** (Python puro) — sem chamadas LLM para decisões críticas. Apenas a síntese final é gerada com LLM, e é ancorada nos fatos retornados.

### Limitações Técnicas Conhecidas
1. **VLM lê apenas 1ª página do PDF**: Notas com múltiplas páginas podem perder dados de páginas subsequentes.
2. **Janela D-2**: Notas emitidas após D-2 não aparecem na exportação e recebem status `FORA_DA_JANELA_IMPORTACAO` (recomenda-se aguardar próxima exportação).
3. **Correspondência manual de pedidos**: A correspondência entre nota (VLM extraída) e pedido (exportação) é baseada em campos chave (`data_emissao`, `valor_total`, `cnpj_cpf_prestador`); em caso de múltiplos pedidos com mesmo valor no mesmo dia, pode haver ambiguidade (raro).

---

## 📂 Estrutura do Projeto

```
health-refund-assistant/
├── README.md                           # Este arquivo
├── .gitignore                          # Exclui .env, dados reais, cache
├── .env.example                        # Template de variáveis de ambiente
├── requirements.txt                    # Dependências (openai, pydantic, etc.)
│
├── docs/                               # Documentação oficial
│   ├── caderno_projeto.md              # Relatório técnico final (R1–R5)
│   ├── planilha_testes_5_casos.md      # Tabela dos 5 casos de teste obrigatórios
│   └── ...
│
├── src/                                # Código principal
│   ├── assistant.py                    # CLI interativo (input nota → output rastreabilidade)
│   ├── web_app.py                      # FastAPI web interface (upload PDF → JSON resposta)
│   ├── vlm_extractor.py                # Extração VLM com schema JSON (gpt-4o-mini)
│   ├── reconciliation.py               # Conciliação determinística contra exportação
│   ├── assessment.py                   # Auditoria pré-envio (completude + 365 dias)
│   ├── paths.py                        # Configuração centralizada de caminhos
│   ├── config.py                       # Variáveis de ambiente (OpenAI, LM Studio, etc.)
│   └── utils.py                        # Funções auxiliares (logging, conversão, etc.)
│
├── prompts/                            # Versões de prompts (versionadas)
│   ├── extraction/
│   │   ├── v1.0.txt                    # Extração inicial (fields basics)
│   │   ├── v2.0.txt                    # Versão 2 (few-shot JSON)
│   │   └── v3.0.txt                    # Versão 3 (schema com validação)
│   └── reembolso_assistente/
│       └── v1.0.txt                    # Síntese da resposta ao usuário (ancorada em fatos)
│
├── json/                               # Contratos JSON (organizados por tipo/processo)
│   ├── README.md                       # Índice de tipos JSON
│   ├── schemas/                        # Definições de estrutura
│   │   ├── README.md
│   │   ├── extraction_nota_fiscal.json # Schema para extração de nota fiscal
│   │   ├── reconciliation_result.json  # Schema para resultado de conciliação
│   │   └── ...
│   ├── extraction/                     # Dados extraídos de notas
│   │   └── README.md
│   ├── reconciliation/                 # Resultados de conciliação
│   │   └── README.md
│   ├── plan/                           # Exportação do plano (ingestion)
│   │   ├── imports/                    # JSONs importados do portal
│   │   │   └── exportacao_plano.md     # Documentação da exportação
│   │   └── processed/                  # Dados processados/normalizados
│   └── evaluation/                     # Resultados de avaliação
│       └── reports/                    # Relatórios JSON (versão prompts)
│
├── data/                               # Dados (sintéticos no Git, reais locais)
│   ├── sinteticos/                     # Dados de teste (fixtures)
│   │   ├── documentos/                 # 15 PDFs sintéticos (C01–C15)
│   │   └── gabaritos.json              # Ground truth esperado (extração, resultado)
│   └── processed/                      # Notas processadas (local, não versionado)
│
├── tests/                              # Testes unitários
│   ├── test_vlm_extractor.py           # Testes de extração VLM
│   ├── test_reconciliation.py          # Testes de conciliação determinística
│   ├── test_assessment.py              # Testes de auditoria pré-envio
│   ├── test_integration.py             # Testes de fluxo completo
│   └── conftest.py                     # Fixtures de teste
│
└── scripts/                            # Scripts utilitários
    ├── gerar_fixtures_sinteticas.py    # Gera 15 PDFs e gabaritos de teste
    └── case_evaluation.py              # Avaliação das versões de prompts (v1–v3)
```

---

## 📊 5 Casos de Teste Obrigatórios

Todos cobertos pela suíte de testes (`tests/`) e avaliação (`case_evaluation.py`):

| Caso | Entrada | Modo | Resultado Esperado |
|------|---------|------|-------------------|
| **C1: Pago Integralmente** | Nota ≤ D-2, dentro de 1 ano, com CRM e descrição | Conciliação | Status `PAGO` com valor confirmado |
| **C2: Pago Parcial / Glosa** | Nota ≤ D-2, parcialmente reembolsada | Conciliação | Status `PAGO_PARCIAL`, valor glosa apurado |
| **C3: Fora da Janela** | Nota > D-2 (emitida após corte) | Auditoria | Status `FORA_DA_JANELA_IMPORTACAO`, recomenda aguardar |
| **C4: Incompleto / Fora do Prazo** | CRM ausente ou > 365 dias | Auditoria | Rejeição com mensagem de campo faltante ou prazo vencido |
| **C5: Prompt Injection** | Descrição contém tentativa de manipulação de prompt | Ambos | Zero falhas críticas; extração e conciliação ignoram tentativa |

---

## 🛠️ Desenvolvimento

### Adicionar Novo Caso de Teste Sintético
1. Crie um PDF em `data/sinteticos/documentos/C##_descricao.pdf`.
2. Adicione gabarito esperado em `data/sinteticos/gabaritos.json`.
3. Execute `pytest -v` e `case_evaluation.py` para validar.

### Versionar Novo Prompt
1. Crie `prompts/extraction/v4.0.txt` (ou nova versão).
2. Atualize `src/vlm_extractor.py` para suportar `prompt_version=v4.0`.
3. Avalie com `case_evaluation.py --models v3.0 v4.0`.
4. Documente mudança em `docs/caderno_projeto.md`.

### Integrar Nova Fonte de Dados (Plano)
1. Exporte dados do portal em JSON (formato padronizado).
2. Coloque em `json/plan/imports/`.
3. Registre schema em `json/schemas/`.
4. Atualize `reconciliation.py` para carregar novo arquivo.
5. Adicione teste de conciliação em `tests/test_reconciliation.py`.

---

## 📞 Contato e Referências

- **Autor**: Fernando Quinnino (fernandoquinino-ntx)
- **Repositório**: [github.com/fernandoquinino-ntx/health-refund-assistant](https://github.com/fernandoquinino-ntx/health-refund-assistant)
- **Trabalho Final**: Opção A (Código + Documentação), Entrega: 02/12/2026

---

## 📝 Licença

MIT License — Use livremente para fins educacionais e comerciais, mantendo atribuição.

---

**Última atualização**: 2025 (Fase 2 — Reescrita Técnica Completa)
