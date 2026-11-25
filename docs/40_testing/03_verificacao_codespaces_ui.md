"""
Verificação Completa com Codespaces + UI + Casos de Teste

Procedimento para validar tudo antes de 02/12/2026
"""

# docs/04_testing/03_verificacao_codespaces_ui.md

## 🧪 Verificação Completa com Codespaces + UI + Testes

**Objetivo:** Validar que tudo funciona end-to-end no Codespaces

---

## Pré-requisitos

✅ ZIP descompactado  
✅ Leu docs/01_quickstart/01_comece_aqui.md  
✅ OPENAI_API_KEY configurada

---

## Etapa 1: Criar Codespaces

```bash
# GitHub > Code > Codespaces > Create codespace on main
# Tempo: 2-3 minutos (auto-setup)

# Verificar que está pronto:
python --version          # 3.12
pip list | grep openai    # Deve aparecer
echo $MODEL_PREFERENCE    # GPT-6 Luna
```

---

## Etapa 2: Executar Testes Unitários (60 testes)

```bash
# Todos os testes
pytest -v

# Com rastreamento automático (RECOMENDADO)
python scripts/test_tracker.py --mode run --verbose

# Tempo esperado: 1-2 minutos
# Resultado esperado: 60/60 ✅
# Logs: json/evaluation/reports/test_execution_*.json
```

---

## Etapa 3: Iniciar UI (Streamlit)

```bash
# Terminal 1 (deixar rodando)
streamlit run src/health_refund_assistant/web_app.py

# Output esperado:
# You can now view your Streamlit app in your browser.
# Local URL: http://localhost:8501
# Network URL: http://...
```

---

## Etapa 4: Testar UI com 5 Casos Reais

**Acesse:** http://localhost:8501

### Caso 1: Nota Padrão (Paga Integralmente)

1. **Upload PDF:**
   - Selecionar: `data/sinteticos/C01_*.pdf`
   - (PDF sintético já existe)

2. **Selecionar Exportação:**
   - Dropdown: "Exportação Padrão" (ou conforme disponível)

3. **Clicar:** "Analisar Nota Fiscal"

4. **Resultado Esperado:**
   ```
   Status: ✅ ENCONTRADO - PAGO INTEGRAL
   Valor: R$ XXX.XX
   Resposta: "Sua nota foi paga integralmente..."
   ```

### Caso 2: Nota com Glosa (Paga Parcialmente)

1. **Upload PDF:**
   - Selecionar: `data/sinteticos/C02_*.pdf`

2. **Resultado Esperado:**
   ```
   Status: ⚠️ ENCONTRADO - PAGO PARCIAL
   Glosa: R$ XXX.XX
   Diferença: R$ XXX.XX
   Resposta: "Sua nota teve glosa de..."
   ```

### Caso 3: Nota Fora da Janela (D-2)

1. **Upload PDF:**
   - Selecionar: `data/sinteticos/C03_*.pdf`

2. **Resultado Esperado:**
   ```
   Status: ⏳ FORA DA JANELA DE IMPORTAÇÃO
   Motivo: Nota emitida após corte da exportação
   Data Corte: D-2
   Resposta: "Sua nota está fora da janela..."
   ```

### Caso 4: Nota com Campos Incompletos

1. **Upload PDF:**
   - Selecionar: `data/sinteticos/C04_*.pdf`
   - (Faltando CRM ou descrição)

2. **Resultado Esperado:**
   ```
   Status: ⚠️ NÃO ENCONTRADO - INCOMPLETO
   Campos Faltantes: CRM, Descrição
   Resposta: "Faltam dados para submissão..."
   ```

### Caso 5: Nota com Prompt Injection (Adversarial)

1. **Upload PDF:**
   - Selecionar: `data/sinteticos/C05_*.pdf`
   - (Contém tentativa de Prompt Injection)

2. **Resultado Esperado:**
   ```
   Status: ✅ PROCESSADO COM SEGURANÇA
   Injection Bloqueada: Sim
   Resposta: "Sua nota foi processada com segurança..."
   (Sem execução da injeção)
   ```

---

## Etapa 5: Revisar Logs de Testes

```bash
# Terminal 2 (novo)

# Ver último relatório JSON
cat json/evaluation/reports/test_execution_*.json | jq .

# Ver logs estruturados
cat json/evaluation/reports/test_tracker_*.log

# Exemplo de output:
# {
#   "timestamp": "2026-11-25T19:00:00",
#   "ambiente": "GitHub Codespaces (manual)",
#   "total_testes": 60,
#   "testes_passaram": 60,
#   "testes_falharam": 0,
#   "resultados": [...]
# }
```

---

## Etapa 6: Executar Avaliação com GPT-6 Luna (Opcional)

```bash
# Executar avaliação dos 5 casos com modelo
python scripts/case_evaluation_v3.py

# Tempo: 2-3 minutos
# Resultado: json/evaluation/reports/avaliacao_5_casos_v4_gpt6luna.json
```

---

## Checklist de Verificação Completa

- [ ] **Codespaces**
  - [ ] Python 3.12 ✅
  - [ ] Dependências instaladas ✅
  - [ ] GPT-6 Luna configurado ($MODEL_PREFERENCE) ✅

- [ ] **Testes Unitários**
  - [ ] 60 testes executados ✅
  - [ ] 100% PASSANDO ✅
  - [ ] Logs salvos em json/evaluation/reports/ ✅

- [ ] **UI (Streamlit)**
  - [ ] Iniciou sem erros ✅
  - [ ] Acessível em http://localhost:8501 ✅

- [ ] **Casos de Teste na UI**
  - [ ] C01 (Pago integral): Status correto ✅
  - [ ] C02 (Pago parcial): Glosa calculada ✅
  - [ ] C03 (Fora janela): Status D-2 ✅
  - [ ] C04 (Incompleto): Campos identificados ✅
  - [ ] C05 (Injection): Bloqueado com segurança ✅

- [ ] **Logs e Relatórios**
  - [ ] test_execution_*.json gerado ✅
  - [ ] test_tracker_*.log gerado ✅
  - [ ] Dados estruturados (timestamp, status, output) ✅

- [ ] **Documentação**
  - [ ] docs/INDEX.md lido ✅
  - [ ] docs/caderno_projeto.md revisado ✅
  - [ ] docs/planilha_testes_5_casos.md conferido ✅

---

## Erros Comuns e Soluções

### Erro: "OPENAI_API_KEY não configurada"

```bash
# Verificar
echo $OPENAI_API_KEY

# Se vazio, configurar no Codespaces:
# GitHub > Codespaces > ... > Secrets > OPENAI_API_KEY
# OU local: cat .env (deve ter OPENAI_API_KEY=sk-...)
```

### Erro: "Port 8501 already in use"

```bash
# Encontrar processo
lsof -i :8501

# Matar e reiniciar
pkill -f streamlit
streamlit run src/health_refund_assistant/web_app.py
```

### Erro: "Module not found: health_refund_assistant"

```bash
# Reinstalar em modo dev
pip install -e .
```

### Erro: "PDF não pode ser processado"

```bash
# Verificar que PDF existe
ls data/sinteticos/C0*.pdf

# Se não existir, gerar
python scripts/gerar_fixtures_sinteticas.py
```

---

## Tempo Esperado

| Etapa | Tempo |
|-------|-------|
| Auto-setup Codespaces | 2-3 min |
| Testes Unitários (60) | 1-2 min |
| UI Streamlit (iniciar) | 1 min |
| Casos de Teste (5×) | 2-3 min |
| Avaliação com GPT-6 | 2-3 min |
| **Total** | **~12-15 min** |

---

## Resultado Final

**Se tudo passou:**

```
✅ Codespaces: Funcional
✅ Testes: 60/60 PASSANDO
✅ UI: Respondendo corretamente
✅ Casos: 5/5 validados
✅ Logs: Rastreamento automático
✅ Pronto para 02/12/2026
```

---

## Próximos Passos

1. Documentar resultado dos testes
2. Revisar docs/caderno_projeto.md (R1-R5)
3. Revisar docs/planilha_testes_5_casos.md
4. Preparar apresentação
5. Entregar 02/12/2026

---

**Documento:** docs/04_testing/03_verificacao_codespaces_ui.md  
**Data:** 25 de novembro de 2026  
**Status:** 🟢 PRONTO PARA USO
