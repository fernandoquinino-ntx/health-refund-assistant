# Pipeline de treinamento visual no Codespaces e GitHub

Este guia descreve o fluxo completo sem enviar PDFs reais ao Git.

## 1. Preparar no Codespaces

1. Abra o Codespace criado a partir do branch.
2. Aguarde `postCreateCommand` instalar `.venv-treinamento`, baixar SmolVLM e
   preparar o Label Studio.
3. Execute OCR e construa o dataset privado em `data/treinamento/dataset/`.
4. Rode a interface do Label Studio e revise cada caixa visualmente.
5. Execute `PYTHONPATH=src .venv/bin/python -m treinamento_visual.train.check_dataset`.

### Comandos mínimos

Coloque PDFs ou imagens em `data/treinamento/entrada/` e execute:

```bash
PYTHONPATH=src .venv-treinamento/bin/python -m treinamento_visual.ingest
```

Inicie o Label Studio local:

```bash
PYTHONPATH=src .venv-treinamento/bin/python \
  -m treinamento_visual.label.cli start --port 8080
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
PYTHONPATH=src .venv/bin/python -m treinamento_visual.train.build_dataset
PYTHONPATH=src .venv/bin/python \
  -m treinamento_visual.train.check_dataset
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
PUBLICAR_DATASET=1 PYTHONPATH=src .venv/bin/python \
  -m treinamento_visual.train.export_public_dataset
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

No Codespace com ambiente MLX, execute:

```bash
.venv-treinamento/bin/mlx_vlm.train \
  --task vlm --algorithm sft --model models/base-smol \
  --data data/treinamento/dataset \
  --train-split train --validation-split valid \
  --train-type lora --lora-rank 16 --lora-alpha 32 \
  --batch-size 1 --max-seq-length 2048 --iters 24 \
  --output-path models/adapters/smolvlm-melhorado/adapters.safetensors
```

Compare o adaptador no conjunto `test` antes de ativar
`LOCAL_VLM_MODEL` ou `LOCAL_VLM_ADAPTER` na aplicação.
