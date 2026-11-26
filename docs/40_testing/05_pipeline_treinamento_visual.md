# Pipeline de treinamento visual no Codespaces e GitHub

Este guia descreve o fluxo completo sem enviar PDFs reais ao Git.

## Conceitos essenciais

- **Modelo base:** entende imagens e texto em geral. Neste projeto é o
  [SmolVLM-256M-Instruct](https://huggingface.co/HuggingFaceTB/SmolVLM-256M-Instruct).
- **Adaptador/LoRA:** arquivo pequeno que ensina preferências e formatos
  específicos do projeto. Ele não substitui todo o modelo.
- **Label/anelação:** desenhar uma caixa na página e transcrever o valor que
  está visível. Isso cria o gabarito usado no treino.
- **Dataset:** conjunto organizado em treino, validação e teste. Cada exemplo
  contém imagem, instrução e resposta JSON revisada.
- **Teste reservado:** documentos nunca usados no treino, usados apenas para
  medir se o adaptador realmente aprendeu.
- **Aprovação:** gate obrigatório. Só um adaptador aprovado vira GGUF ativo no
  Codespaces.

Terminologia prática:

```text
PDF real
  -> imagem privada
  -> OCR auxiliar
  -> caixa + transcrição = label
  -> JSONL
  -> treino
  -> adaptador
  -> avaliação reservada
  -> aprovação
  -> fusão + GGUF
  -> llama.cpp no Codespaces
```

## 1. Preparar no Codespaces

1. Abra o Codespace criado a partir do branch.
2. Aguarde `postCreateCommand` instalar `.venv-treinamento`, preparar llama.cpp,
   baixar o modelo SmolVLM Hugging Face e configurar o Label Studio.
3. Execute OCR e construa o dataset privado em `data/treinamento/dataset/`.
4. Rode a interface do Label Studio e revise cada caixa visualmente.
5. Execute `make check-dataset`.

### Comandos mínimos

Coloque PDFs ou imagens em `data/treinamento/entrada/` e execute:

```bash
make ingest
```

Inicie o Label Studio local:

```bash
make label-studio
```

Abra `http://localhost:8080`. Na primeira execução:

1. Clique em **Sign up** e crie a conta local.
2. Crie um projeto chamado `Notas fiscais - treino visual`.
3. No projeto, abra **Settings → Labeling Interface** e confirme os nove rótulos
   definidos em `src/treinamento_visual/label/config.xml`.
4. Importe `data/treinamento/label_studio/tarefas.json`.
5. Abra **Label All Tasks**.

### Fazer os labels

Em cada tarefa:

1. Confira a imagem inteira.
2. Selecione o rótulo correto.
3. Desenhe um retângulo em torno do valor visível, não do título.
4. Preencha a transcrição correspondente na região.
5. Repita para cada campo visível.
6. Clique em **Submit**.
7. Para uma página sem campos confiáveis, envie uma anotação vazia somente
   depois da revisão humana. Não marque valores que não estejam legíveis.

Quando todas as tarefas tiverem sido revisadas:

```bash
make build-dataset
make check-dataset
```

O build cria separações por documento em:

- `data/treinamento/dataset/train.jsonl`
- `data/treinamento/dataset/valid.jsonl`
- `data/treinamento/dataset/test.jsonl`

## 2. Revisar antes de publicar

Não publique nomes, CPF, chaves fiscais, endereços, emails ou outros dados
sensíveis. Cubra ou substitua os dados visuais antes de copiar o dataset.

Marque em `json/training/visual/consentimento_publicacao.json` somente depois
da revisão humana:

```json
{
  "aprovado": true,
  "responsavel": "nome-ou-identificador-aprovado",
  "data_aprovacao": "AAAA-MM-DD",
  "anonimizacao_revisada": true,
  "observacao": "Dados revisados e anonimizados."
}
```

O exportador não ignora esses campos. Ele também exige `PUBLICAR_DATASET=1`.

```bash
make export-dataset
```

Saída:

- `json/training/visual/dataset/train.jsonl`
- `json/training/visual/dataset/valid.jsonl`
- `json/training/visual/dataset/test.jsonl`
- `json/training/visual/images/`

## 3. Commit e push

Faça commit somente dos JSONL aprovados, imagens anonimizadas e consentimento
aprovado. Alterações em `json/training/visual/dataset/**` disparam o workflow
`.github/workflows/treinar_modelo_visual.yml`.

O workflow valida o consentimento, treina um LoRA curto no runner Ubuntu,
executa uma inferência de verificação e publica `modelo_visual_treinado`
como artefato de Actions. Não faz commit automático de pesos nem dados.

## 4. Treino manual

No Mac, execute o treino local curto com:

```bash
make train-mac
```

Compare o adaptador no conjunto `test`, gere o relatório de aprovação e execute
`make evaluate-adapter`, `make approve-adapter` e `make convert`.
O adaptador só é ativado no Codespaces quando `modelo_aprovado.json` contém
`aprovado=true`.

## 5. Novo ciclo com mais documentos

Quando quiser melhorar o modelo:

1. Coloque PDFs ou imagens em `data/treinamento/entrada/`.
2. Execute `make ingest`.
3. Abra o Label Studio com `make label-studio`.
4. Rotule os novos documentos e revise visualmente todos os rótulos.
5. Execute `make build-dataset`.
6. Execute `make check-dataset`.
7. Treine novamente com `make train-mac` ou pelo workflow GitHub.
8. Execute `make evaluate-adapter`.
9. Execute `make approve-adapter`.
10. Se o relatório aprovar, marque manualmente o estado aprovado.
11. Execute `make convert`.
12. Reinicie o Codespace. O assistente ativa o GGUF aprovado automaticamente.

### Aprovar o adaptador

Edite `json/training/visual/modelo_aprovado.json` somente depois de revisar o
relatório de avaliação:

```json
{
  "aprovado": true,
  "documentos_testados": 10,
  "base_taxa_acerto": 0.40,
  "adaptado_taxa_acerto": 0.75,
  "ganho": 0.35
}
```

Números apenas ilustrativos. O adaptador deve melhorar a taxa reservada, reduzir
alucinações e manter JSON válido. Não marque aprovado por aparência da interface
ou pela loss do treino.
### Resultado atual conhecido

O modelo 256M base foi convertido para GGUF Q4_K_M e o servidor multimodal
llama.cpp respondeu com HTTP 200. O LoRA privado de 12 iterações foi convertido
para GGUF e testado junto da base no documento reservado, mas não produziu JSON
útil. Por isso `modelo_aprovado.json` permanece `aprovado=false`.
