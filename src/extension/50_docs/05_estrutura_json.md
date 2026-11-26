# 5. Estrutura JSON – Formato dos Dados

> Este guia descreve a implementação fonte em `src/extension/`. O
> [contrato atual da exportação](../../../json/plan/schemas/plan_export.schema.json)
> é a referência para importação na aplicação.

## Visão Geral

O JSON exportado segue este padrão:

```json
{
  "coleta_realizada_em": "2026-11-25T20:00:00",
  "total": 5,
  "totalPorPessoa": {"João": 2, "Maria": 3},
  "pessoas": ["João", "Maria"],
  "reembolsos": [ ... ],
  "erros": []
}
```

---

## Raiz: Metadados

| Campo | Tipo | Exemplo | Descrição |
|-------|------|---------|-----------|
| `coleta_realizada_em` | ISO 8601 | `2026-11-25T20:00:00` | Timestamp da coleta |
| `total` | Número | `5` | Total de reembolsos coletados |
| `totalPorPessoa` | Objeto | `{"João": 2, "Maria": 3}` | Contagem por beneficiário |
| `pessoas` | Array | `["João", "Maria"]` | Lista de pessoas consultadas |
| `reembolsos` | Array | `[{...}, {...}]` | Array de reembolsos (veja abaixo) |
| `erros` | Array | `["Erro ao coletar João: timeout"]` | Problemas encontrados |

---

## Reembolsos: Estrutura Completa

Cada item em `reembolsos` contém:

```json
{
  "pessoaConsultada": "João Silva",
  "numeroSinistro": "123456",
  "beneficiario": "João Silva",
  "status": "PAGO",
  "prestador": "HOSPITAL XYZ LTDA",
  "cobertura": "INTERNAÇÃO HOSPITALAR",
  "dataSolicitacao": "2026-11-15",
  "dataRealizacao": "2026-11-14",
  "dataPagamento": "2026-11-20",
  "origemDocumento": "RECIBO",
  "valorSolicitado": 5000.00,
  "valorSolicitadoNum": 5000.00,
  "valorCoparticipacao": 500.00,
  "valorCoparticipacaoNum": 500.00,
  "valorFinalReembolsado": 4500.00,
  "valorFinalReembolsadoNum": 4500.00,
  "descricao": "Internação 3 dias - Cirurgia de apêndice",
  "formaPagamento": "CREDITO",
  "procedimento": "APENDICECTOMIA",
  "informacaoAdicional": "Autorizado previamente",
  "camposBrutos": {
    "Rótulo 1": "Valor 1",
    "Rótulo 2": "Valor 2"
  },
  "linhaLista": {
    "coluna1": "...",
    "coluna2": "..."
  },
  "subItens": [
    {"descricao": "Diária 1", "valor": 1500.00},
    {"descricao": "Diária 2", "valor": 1500.00},
    {"descricao": "Diária 3", "valor": 1500.00}
  ]
}
```

---

## Campos Detalhados

### Identificação

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `pessoaConsultada` | String | Beneficiário consultado (do dropdown) |
| `numeroSinistro` | String | ID único do sinistro no portal |
| `beneficiario` | String | Beneficiário associado (pode diferir de consultada) |

### Status e Datas

| Campo | Tipo | Exemplo | Descrição |
|-------|------|---------|-----------|
| `status` | String | `PAGO`, `PARCIAL`, `RECUSADO`, `EM_ANALISE` | Status do reembolso |
| `dataSolicitacao` | YYYY-MM-DD | `2026-11-15` | Quando foi solicitado |
| `dataRealizacao` | YYYY-MM-DD | `2026-11-14` | Quando ocorreu o serviço |
| `dataPagamento` | YYYY-MM-DD | `2026-11-20` | Quando foi pago |

### Valores (Duplicados: String + Num)

| Campo | Tipo | Exemplo | Notas |
|-------|------|---------|-------|
| `valorSolicitado` | String ou Número | `"5000.00"` ou `5000.00` | Valor solicitado ao plano |
| `valorSolicitadoNum` | Número | `5000.00` | Versão numérica (garantida) |
| `valorCoparticipacao` | String ou Número | `"500.00"` | Coparticipação do beneficiário |
| `valorCoparticipacaoNum` | Número | `500.00` | Versão numérica |
| `valorFinalReembolsado` | String ou Número | `"4500.00"` | Valor efetivamente reembolsado |
| `valorFinalReembolsadoNum` | Número | `4500.00` | Versão numérica |

**Dica:** Sempre use campos `...Num` para cálculos matemáticos.

### Descrição e Procedimento

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `descricao` | String | Descrição completa do serviço |
| `cobertura` | String | Tipo de cobertura (INTERNAÇÃO, CONSULTA, etc) |
| `procedimento` | String | Código ou nome do procedimento médico |
| `prestador` | String | Nome da clínica/hospital |

### Dados Adicionais

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `origemDocumento` | String | RECIBO, NOTA FISCAL, DECLARAÇÃO, etc |
| `formaPagamento` | String | CREDITO, DOC, TED, DINHEIRO, etc |
| `informacaoAdicional` | String | Notas adicionais do plano |
| `camposBrutos` | Objeto | Todos os rótulos/valores da tela (como lidos) |
| `linhaLista` | Objeto | Dados brutos da linha da tabela |
| `subItens` | Array | Se houver sub-itens (ex: diárias de internação) |

---

## Exemplo Real: Internação com Sub-itens

```json
{
  "numeroSinistro": "999999",
  "descricao": "Internação Hospital Central",
  "dataSolicitacao": "2026-11-15",
  "dataRealizacao": "2026-11-14",
  "valorSolicitado": 4500.00,
  "valorFinalReembolsado": 4050.00,
  "subItens": [
    {
      "descricao": "Diária Enfermaria - 14/11",
      "valor": 1500.00
    },
    {
      "descricao": "Diária Enfermaria - 15/11",
      "valor": 1500.00
    },
    {
      "descricao": "Diária Enfermaria - 16/11",
      "valor": 1500.00
    }
  ]
}
```

---

## Validação

Ao importar uma exportação, a aplicação valida o JSON com o schema:
```
json/plan/schemas/plan_export.schema.json
```

**Use para:**
- ✅ Validar importação na aplicação
- ✅ Conferir a estrutura esperada, sem garantir a veracidade dos dados
- ✅ Debugar campos faltantes

---

## Próximo

- **Troubleshooting:** [`07_troubleshooting.md`](./07_troubleshooting.md)
- **Desenvolvimento:** [`08_desenvolvimento.md`](./08_desenvolvimento.md)
- **Uso Básico:** [`03_uso_basico.md`](./03_uso_basico.md)
