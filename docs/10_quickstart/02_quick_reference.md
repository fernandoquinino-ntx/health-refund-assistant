# Quick Start — Health Refund Assistant

## Clone e Prepare
```bash
unzip health-refund-assistant-entrega.zip -d health-refund-assistant
cd health-refund-assistant
cp .env.example .env  # Edite com sua OPENAI_API_KEY
```

## Instale e Teste
```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
pytest -v  # Esperado: 60+ testes passando
```

## Execute
```bash
# CLI interativo
python3 src/health_refund_assistant/assistant.py

# Ou web app (Streamlit)
streamlit run src/health_refund_assistant/web_app.py
# Acesse: http://localhost:8501
```

## Avalie Versões (com API key)
```bash
export OPENAI_API_KEY=sk-...
.venv/bin/python scripts/case_evaluation.py --prompt-version v4.0
# Resultados em: json/evaluation/reports/
```

## Leia a Documentação
- **README.md** — Visão geral técnica, D-1/D-2, fluxo
- **docs/caderno_projeto.md** — Requisitos R1–R5 (Problema, Prompt, IA, Testes, Segurança)
- **docs/planilha_testes_5_casos.md** — Tabela dos 5 casos obrigatórios (C01–C05)
- **DELIVERY_CHECKLIST.md** — Verificação de entrega

## Estrutura Chave
```
src/health_refund_assistant/
├── assistant.py          # Orquestrador (3 etapas)
├── vlm_extractor.py      # Extração VLM (GPT-6 Luna + schema)
├── reconciliation.py     # Lógica determinística
├── assessment.py         # Auditoria pré-envio + janela D-2
└── web_app.py            # Interface Streamlit

docs/
├── caderno_projeto.md    # R1–R5 (Problema, Prompt, IA, Testes, Segurança)
└── planilha_testes_5_casos.md  # Tabela C01–C05

json/tests/synthetic/
├── gabarito.json         # Ground truth esperado
└── casos_teste.json      # Descrição dos 15 casos

data/sinteticos/documentos/
└── C01.pdf–C15.pdf       # 15 PDFs sintéticos de teste
```

## Dados Sintéticos
- **C01**: Pago Integralmente
- **C02**: Pago Parcial / Glosa
- **C03**: Fora da Janela D-2
- **C04**: Incompleto / Fora do Prazo (365 dias)
- **C05**: Adversarial / Prompt Injection
- **C06–C15**: Variações e edge cases

## Fluxo de Execução
```
PDF → VLM Extractor → Verificação Determinística → LLM Síntese → Resposta Usuário
      (extrai)        (D-2 + 365d + completude)   (ancorada)
```

---

**Status**: ✅ Pronto para entrega (25 de Novembro de 2025)  
**Versão**: 1.0
