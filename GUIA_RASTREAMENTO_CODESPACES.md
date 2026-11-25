# 🧪 Rastreamento de Testes no Codespaces

**Status:** ✅ Pronto para você executar manualmente no Codespaces  
**Rastreamento:** Automático — tudo será logado  
**Versão:** 1.0

---

## 🎯 Objetivo

Você vai **executar todos os testes manualmente no Codespaces** (você está em controle), e eu vou **rastrear/logar cada teste** automaticamente. Assim você pode:

✅ Ver os testes rodando em tempo real  
✅ Conferir o progresso no console  
✅ Ter logs salvos para auditoria  
✅ Gerar relatório JSON com resultados

---

## 📋 Pré-requisitos (Já Configurado)

✅ `.devcontainer/devcontainer.json` → Auto-install dependências + fixtures  
✅ `scripts/test_tracker.py` → Sistema de rastreamento (novo!)  
✅ `pytest` + `python-json-report` → Captura de logs JSON  
✅ `json/evaluation/reports/` → Diretório para salvar logs

---

## 🚀 Como Usar no Codespaces

### **Passo 1: Criar Codespaces**

```bash
# GitHub > Code > Codespaces > Create codespace on main
# Aguarde 2-3 minutos (auto-install via post-create command)
```

---

### **Passo 2: Executar Testes com Rastreamento**

#### **OPÇÃO A — Executar TODOS os testes (Recomendado)**

```bash
# Dentro do Codespaces, execute:
python scripts/test_tracker.py --mode run --verbose
```

**Esperado:**
- Console mostra progresso em tempo real
- Cada teste é registrado
- Status final: `✅ 60 TESTES PASSARAM` ou `❌ X TESTES FALHARAM`

**Saída:**
```
╔════════════════════════════════════════════════════════════════════════════╗
║                     RASTREADOR DE TESTES                                   ║
╚════════════════════════════════════════════════════════════════════════════╝

🧪 INICIANDO TESTES: tests
Data/Hora: 2026-11-25T18:00:00.000000
Modo: Verboso
Comando: python -m pytest tests -v --tb=short

[Progresso de testes...]

✅ TESTES PASSARAM!

RESUMO DE EXECUÇÃO
─────────────────────────────────────────────────────────────────────────────
Total de testes: 60
✅ Passaram: 60
❌ Falharam: 0
```

#### **OPÇÃO B — Executar Teste Específico**

```bash
# Teste apenas C01 (Pago Integralmente):
python scripts/test_tracker.py --mode test --name tests/test_reconciliation.py::test_case_01_pago_integralmente

# Teste apenas C05 (Prompt Injection):
python scripts/test_tracker.py --mode test --name tests/test_vlm_extractor.py::test_case_05_adversarial_prompt_injection
```

---

### **Passo 3: Revisar Logs e Relatórios**

Depois de executar os testes, os arquivos são salvos em:

```bash
# 📊 Relatório JSON com resultados
cat json/evaluation/reports/test_execution_*.json

# 📋 Log completo de texto
cat json/evaluation/reports/test_tracker_*.log

# 🧪 Relatório nativo pytest (se instalado pytest-json-report)
cat json/evaluation/reports/pytest_report.json
```

---

### **Passo 4: Gerar Relatório Final**

```bash
# Após os testes, gere o relatório consolidado:
python scripts/test_tracker.py --mode report
```

Isso vai:
- Consolidar todos os resultados
- Exibir resumo no console
- Salvar JSON estruturado

---

## 📊 Arquivos de Rastreamento

Depois que você executar os testes, vão aparecer em `json/evaluation/reports/`:

| Arquivo | Conteúdo |
|---------|----------|
| `test_execution_YYYYMMDD_HHMMSS.json` | ⭐ Relatório estruturado (PRINCIPAL) |
| `test_tracker_YYYYMMDD_HHMMSS.log` | Log de texto completo |
| `pytest_report.json` | Relatório JSON nativo do pytest |

**Exemplo de `test_execution_*.json`:**
```json
{
  "timestamp": "2026-11-25T18:00:00.000000",
  "ambiente": "GitHub Codespaces (manual)",
  "total_testes": 60,
  "testes_passaram": 60,
  "testes_falharam": 0,
  "resultados": [
    {
      "timestamp": "2026-11-25T18:00:05.000000",
      "status": "PASSOU",
      "return_code": 0,
      "command": "python -m pytest tests -v --tb=short",
      "duration": "~1-2 min"
    }
  ],
  "arquivos_relacionados": ["pytest_report.json", "test_tracker_*.log"]
}
```

---

## 🎯 Fluxo Completo (Resumo)

```
1. GitHub Codespaces
   ├─ Criar codespace (2-3 min auto-setup)
   └─ Python 3.12 + dependências prontas

2. Executar Testes com Rastreamento
   ├─ python scripts/test_tracker.py --mode run
   ├─ Console mostra progresso ✅
   └─ Logs salvos automaticamente 📋

3. Revisar Resultados
   ├─ cat json/evaluation/reports/test_execution_*.json
   ├─ Conferir status (PASSOU / FALHOU)
   └─ Relatório está pronto para auditoria

4. Gerar Relatório Final
   ├─ python scripts/test_tracker.py --mode report
   └─ Resumo consolidado salvo
```

---

## ✅ Garantias

✅ **Você está em controle total**  
   └─ Executa quando quiser, quantas vezes quiser

✅ **Rastreamento automático**  
   └─ Sem fazer nada extra, tudo é capturado

✅ **Logs estruturados**  
   └─ JSON para análise programática, .log para leitura

✅ **Auditável**  
   └─ Timestamp, return code, output completo registrados

✅ **Codespaces funcional**  
   └─ App sobe, testes rodam, tudo é rastreado

---

## 🔍 Monitoramento em Tempo Real

Enquanto os testes rodam no Codespaces, você verá:

```
🧪 INICIANDO TESTES: tests
Data/Hora: 2026-11-25T18:00:00+00:00
Modo: Verboso
Comando: python -m pytest tests -v --tb=short --json-report

[Testes sendo executados...]

tests/test_reconciliation.py::test_case_01_pago_integralmente PASSED   [  2%]
tests/test_reconciliation.py::test_case_02_pago_parcial PASSED         [  4%]
tests/test_assessment.py::test_case_03_fora_janela PASSED              [  6%]
...
tests/test_vlm_extractor.py::test_case_05_adversarial_prompt_injection PASSED [ 100%]

========================= 60 passed in 1.18s =========================

✅ TESTES PASSARAM!

RESUMO DE EXECUÇÃO
─────────────────────────────────────────────────────────────────────────────
Total de testes: 60
✅ Passaram: 60
❌ Falharam: 0
═════════════════════════════════════════════════════════════════════════════
```

---

## 📌 Dicas

### Se um teste falhar:

```bash
# Veja mais detalhes:
python scripts/test_tracker.py --mode test --name <nome_do_teste> --verbose

# Exemplo:
python scripts/test_tracker.py --mode test --name tests/test_reconciliation.py::test_case_01_pago_integralmente
```

### Se quiser apenas um subset:

```bash
# Apenas testes de reconciliação:
python -m pytest tests/test_reconciliation.py -v

# Apenas testes de segurança (injection):
python -m pytest tests/test_vlm_extractor.py -k "adversarial" -v
```

### Exibir log completo:

```bash
# Ver último log gerado:
ls -lh json/evaluation/reports/test_tracker_*.log
tail -100 json/evaluation/reports/test_tracker_*.log
```

---

## ✨ Resultado Esperado

Depois que você executar no Codespaces:

```
✅ 60 testes PASSANDO
✅ Logs salvos em JSON (auditável)
✅ Relatório consolidado
✅ App Streamlit pronta para uso (streamlit run src/health_refund_assistant/web_app.py)
```

---

## 🚀 Próximas Ações

1. **Hoje:** Criar Codespaces e executar `python scripts/test_tracker.py --mode run`
2. **Revisar:** Logs salvos em `json/evaluation/reports/`
3. **Confirmar:** Status final (60/60 testes ou X falhas)
4. **Usar:** App está pronta com `streamlit run web_app.py`

---

**Versão:** 1.0  
**Data:** 2026-11-25  
**Pronto:** ✅ SIM — Execute quando quiser no Codespaces
