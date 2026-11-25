# 📑 Índice de Documentação e Arquivos

## 🚀 Comece Aqui

| Documento | Propósito | Tempo |
|-----------|-----------|-------|
| **[QUICKSTART.md](QUICKSTART.md)** | Guia rápido de 5 minutos | 5 min ⏱️ |
| **[README.md](README.md)** | Visão técnica completa | 15 min 📖 |
| **[DELIVERY_CHECKLIST.md](DELIVERY_CHECKLIST.md)** | Verificação de entrega | 10 min ✅ |

---

## 📚 Documentação Oficial (Trabalho Final)

### R1-R5: Requisitos Técnicos
- **[docs/caderno_projeto.md](docs/caderno_projeto.md)** — Relatório técnico completo
  - R1: Problema e Valor (token/custo estimado)
  - R2: Prompt Engineering (evolução v1.0 → v4.0)
  - R3: Recurso de IA (VLM + Dados Estruturados + LLM Síntese)
  - R4: Testes (5 casos obrigatórios + 15 sintéticos)
  - R5: Segurança e Ética (Prompt Injection, LGPD)

### Tabela de Testes (5 Casos Obrigatórios)
- **[docs/planilha_testes_5_casos.md](docs/planilha_testes_5_casos.md)** — Tabela detalhada
  - C01: Pago Integralmente ✅
  - C02: Pago Parcial / Glosa ✅
  - C03: Fora da Janela D-2 ✅
  - C04: Incompleto / Fora do Prazo ✅
  - C05: Adversarial / Prompt Injection ✅

---

## 🏗️ Código Principal

### Fluxo de Execução (3 Etapas)
```
PDF → VLM Extractor → Verificação Determinística → LLM Síntese → Resposta
```

| Arquivo | Função |
|---------|--------|
| **[src/health_refund_assistant/assistant.py](src/health_refund_assistant/assistant.py)** | Orquestrador das 3 etapas |
| **[src/health_refund_assistant/vlm_extractor.py](src/health_refund_assistant/vlm_extractor.py)** | Extração VLM (gpt-4o-mini + schema strict) |
| **[src/health_refund_assistant/reconciliation.py](src/health_refund_assistant/reconciliation.py)** | Lógica determinística de conciliação |
| **[src/health_refund_assistant/assessment.py](src/health_refund_assistant/assessment.py)** | Auditoria pré-envio + janela D-2 |
| **[src/health_refund_assistant/web_app.py](src/health_refund_assistant/web_app.py)** | Interface Streamlit |

---

## 🧪 Testes

| Arquivo | Descrição |
|---------|-----------|
| **[tests/](tests/)** | Suíte completa de testes unitários (60+ testes, 100% passando) |
| **[data/sinteticos/documentos/](data/sinteticos/documentos/)** | 15 PDFs sintéticos (C01-C15) para teste |
| **[json/tests/synthetic/gabarito.json](json/tests/synthetic/gabarito.json)** | Ground truth esperado |
| **[scripts/gerar_fixtures_sinteticas.py](scripts/gerar_fixtures_sinteticas.py)** | Gerador de fixtures |

---

## 📋 Configuração e Variáveis

| Arquivo | Propósito |
|---------|-----------|
| **[.env.example](.env.example)** | Template de variáveis de ambiente (OPENAI_API_KEY, etc.) |
| **[requirements.txt](requirements.txt)** | Dependências Python |
| **[.gitignore](.gitignore)** | Arquivos não versionados (.env, PDFs reais, etc.) |

---

## 🔧 Schemas e Contatos JSON

### Estrutura de Dados
```
json/
├── schemas/                          # Índice central de schemas
├── extraction/schemas/               # Schemas de extração VLM
├── plan/schemas/                     # Schema da exportação do plano
├── reconciliation/schemas/           # Schema de conciliação e mapping
├── evaluation/schemas/               # Schema de relatórios de avaliação
└── tests/schemas/                    # Schema de casos de teste
```

| Pasta | Conteúdo |
|-------|----------|
| **[json/schemas/](json/schemas/)** | Índice central com documentação |
| **[json/extraction/schemas/](json/extraction/schemas/)** | `vlm_extraction.schema.json`, `vlm_extraction_v4.schema.json` |
| **[json/plan/schemas/](json/plan/schemas/)** | `plan_export.schema.json` |
| **[json/reconciliation/schemas/](json/reconciliation/schemas/)** | `mapping_config.schema.json`, `reconciliation_report.schema.json` |
| **[json/tests/schemas/](json/tests/schemas/)** | `test_cases.schema.json`, `test_gold.schema.json` |

---

## 🎯 Prompts (Versões)

| Versão | Arquivo | Status |
|--------|---------|--------|
| **v1.0** | [prompts/extraction/v1.0.txt](prompts/extraction/v1.0.txt) | Histórico (baseline) |
| **v2.0** | [prompts/extraction/v2.0.txt](prompts/extraction/v2.0.txt) | Histórico (few-shot) |
| **v3.0** | [prompts/extraction/v3.0.txt](prompts/extraction/v3.0.txt) | Schema + Anti-Injeção ✅ |
| **v4.0** | [prompts/extraction/v4.0.txt](prompts/extraction/v4.0.txt) | CRM + Valor Normalizado ✅ |
| **Resposta** | [prompts/reembolso_assistente/v1.0.txt](prompts/reembolso_assistente/v1.0.txt) | Síntese ancorada em fatos |

---

## 📊 Avaliação

| Arquivo | Descrição |
|---------|-----------|
| **[scripts/case_evaluation.py](scripts/case_evaluation.py)** | Script de avaliação de versões (requer OPENAI_API_KEY) |
| **[json/evaluation/reports/](json/evaluation/reports/)** | Relatórios de avaliação (v1.0_results.json, etc.) |

**Uso**:
```bash
export OPENAI_API_KEY=sk-...
python3 scripts/case_evaluation.py --models v1.0 v2.0 v3.0 v4.0
```

---

## 🚀 Execução Rápida

```bash
# 1. Descompactar (se recebeu ZIP)
unzip health-refund-assistant-entrega.zip -d health-refund-assistant
cd health-refund-assistant

# 2. Configurar
cp .env.example .env
# Edite .env e adicione OPENAI_API_KEY

# 3. Instalar e Testar
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
pytest -v  # Esperado: 60+ testes passando

# 4. Usar
python3 src/health_refund_assistant/assistant.py
# Ou:
streamlit run src/health_refund_assistant/web_app.py
```

---

## 📌 Referência Rápida

### Fluxo de Dados
1. **Entrada**: PDF/Imagem de nota fiscal
2. **VLM Extractor**: Extrai campos com schema JSON strict
3. **Verificação Determinística**: Valida D-2 (janela) + 365 dias (prazo) + completude
4. **Conciliação**: Busca na exportação do plano
5. **Síntese LLM**: Gera resposta ancorada em fatos
6. **Saída**: Rastreabilidade comprovada

### Regras Principais
- **D-1**: Corte da exportação do plano (últimos pedidos processados)
- **D-2**: Janela de elegibilidade interna (margem de segurança)
- **365 dias**: Prazo máximo para submissão de pedidos de reembolso
- **Modo 1**: Conciliação Financeira (nota ≤ D-2 encontrada)
- **Modo 2**: Auditoria Pré-Envio (nota ≤ D-2 não encontrada ou > D-2)

### Status Possíveis
- `PAGO`: Reembolso pago integralmente
- `PAGO_PARCIAL`: Reembolso pago com glosa/devolução
- `RECUSADO`: Pedido recusado pelo plano
- `EM_ANALISE`: Pedido ainda sob análise
- `FORA_DA_JANELA_IMPORTACAO`: Nota emitida após D-2
- `nao_localizado_nas_exportacoes`: Nota não encontrada (pode não ter sido enviada)

---

## ✅ Checklist de Verificação

- [ ] Leu QUICKSTART.md
- [ ] Leu README.md
- [ ] Revisou docs/caderno_projeto.md (R1-R5)
- [ ] Revisou docs/planilha_testes_5_casos.md (C01-C05)
- [ ] Executou `pytest -v` (60+ testes passando)
- [ ] Configurou .env com OPENAI_API_KEY
- [ ] Executou `assistant.py` ou `web_app.py`
- [ ] Validou LGPD (sem dados pessoais no ZIP)
- [ ] Revisou commits (5 commits novos)

---

## 📞 Contato

- **Autor**: Fernando Quinnino (@fernandoquinino-ntx)
- **Repositório**: [github.com/fernandoquinino-ntx/health-refund-assistant](https://github.com/fernandoquinino-ntx/health-refund-assistant)
- **Trabalho Final**: Opção A (Código + Documentação), Entrega: 02/12/2026

---

**Versão**: 1.0  
**Data**: 25 de Novembro de 2025  
**Status**: ✅ Pronto para Entrega e Avaliação
