# Care Plus – Coletor de Reembolsos (Chrome MV3)

## Instalar
1. Descompacte o .zip numa pasta.
2. Abra `chrome://extensions`, ligue **Modo do desenvolvedor**.
3. **Carregar sem compactação** → selecione a pasta.

## Usar
1. Faça login no portal Care Plus (qualquer página serve).
2. Clique no ícone da extensão e em **Coletar Reembolsos**. A extensão abre sozinha
   **Consultar Reembolsos** pelo menu do site e percorre **cada beneficiário** da conta, um por vez.
   (Opção "Grupo familiar de uma vez" faz uma única consulta com todos.)
3. Um aviso azul no canto da página mostra o progresso. A exportação JSON vai para Downloads:
   `careplus-reembolsos-AAAAMMDD-HHMM.json` (e `-lmstudio.json` se ativado).

## Como funciona
- Lê a lista de beneficiários (`#lstBeneficiarios`) e, para cada pessoa, chama `passo1` do portal com os dados dela; lê todas as linhas da tabela `#tblAut1` (todas as páginas do DataTable).
- Linhas que abrem sub-itens (`passo2`) são expandidas; cada item tem o detalhe (`passo3`) aberto e lido de `#divDadosPasso3`.
- Atraso aleatório entre cada passo (padrão 1,5–3 s); 1 nova tentativa em caso de falha.
- Período: deixe as datas em branco para usar o da tela, ou informe De/Até — períodos longos são divididos em janelas (padrão 6 meses) e duplicados removidos.

## LM Studio
Ative "Enviar ao LM Studio", informe a URL (padrão `http://localhost:1235`) e o modelo carregado. O JSON vai para `/v1/chat/completions`; a resposta fica dentro de um arquivo JSON `-lmstudio.json`. A chamada sai do service worker da extensão, então não precisa liberar CORS no LM Studio.

## Campos no JSON
Topo: `total`, `totalPorPessoa`, `pessoas`, `reembolsos`, `erros`.
Cada reembolso: `pessoaConsultada, numeroSinistro, beneficiario, status, prestador, cobertura, dataSolicitacao, dataRealizacao, dataPagamento, origemDocumento, valorSolicitado(+Num), valorCoparticipacao(+Num), valorFinalReembolsado(+Num), descricao, formaPagamento, procedimento, informacaoAdicional`, mais `camposBrutos` (todos os rótulos da tela), `linhaLista` e, para sub-itens, `itemLista`.

[`manifest.json`](./manifest.json) é metadado obrigatório da extensão Chrome Manifest V3, não uma
exportação de dados. As exportações baixadas são datasets separados e, quando
importadas na aplicação, são validadas pelo
[`plan_export.schema.json`](../json/plan/schemas/plan_export.schema.json). Consulte também a
[documentação específica do manifesto](./manifest.md) e a
[documentação da exportação JSON](./exportacao_reembolsos.md).
