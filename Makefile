.PHONY: help setup setup-app setup-training setup-conversion setup-label setup-codespace run test test-agent ingest prepare-tasks label-studio build-dataset check-dataset export-dataset train-mac train-ci convert build-extension clean

PYTHON_APP=.venv/bin/python
PYTHON_TRAIN=.venv-treinamento/bin/python
PYTHON_CONVERT=.venv-conversao/bin/python

help:
	@printf "Comandos disponíveis:\n"
	@printf "  make setup             Cria os ambientes principal, treino e conversão\n"
	@printf "  make setup-codespace   Executa a configuração completa do Codespace\n"
	@printf "  make run               Inicia o assistente Streamlit na porta 8501\n"
	@printf "  make test              Executa toda a bateria unittest\n"
	@printf "  make test-agent        Executa testes do agente conversacional\n"
	@printf "  make ingest            Processa PDFs/imagens privadas\n"
	@printf "  make prepare-tasks     Prepara tarefas para o Label Studio\n"
	@printf "  make label-studio      Inicia o Label Studio local\n"
	@printf "  make build-dataset     Converte anotações em JSONL privado\n"
	@printf "  make check-dataset     Valida o dataset visual\n"
	@printf "  make export-dataset    Exporta um dataset aprovado para o Git\n"
	@printf "  make train-mac         Executa LoRA curto no Mac com MLX\n"
	@printf "  make train-ci          Valida o treino preparado para GitHub Actions\n"
	@printf "  make convert           Exporta artefatos GGUF/mmproj\n"
	@printf "  make build-extension   Valida e monta a extensão Chrome\n"
	@printf "  make clean            Remove caches e pacotes gerados localmente\n"

setup: setup-app setup-training setup-conversion setup-label

setup-app:
	python3 -m venv .venv
	$(PYTHON_APP) -m pip install -r requirements/base.txt

setup-training:
	python3 -m venv .venv-treinamento
	$(PYTHON_TRAIN) -m pip install -r requirements/treinamento.txt

setup-conversion:
	python3 -m venv .venv-conversao
	$(PYTHON_CONVERT) -m pip install -r requirements/conversao.txt

setup-label:
	python3 -m venv .venv-label-studio
	$(CURDIR)/.venv-label-studio/bin/python -m pip install -r requirements/label-studio.txt

setup-codespace:
	bash src/treinamento_visual/scripts/setup_codespaces_treinamento.sh

run:
	PYTHONPATH=src STREAMLIT_BROWSER_GATHER_USAGE_STATS=false \
		$(PYTHON_APP) -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501 --server.headless true

test:
	PYTHONPATH=src $(PYTHON_APP) -m unittest discover -s tests -v

test-agent:
	PYTHONPATH=src $(PYTHON_APP) -m unittest tests.unit.10_application.test_agent -v

ingest:
	PYTHONPATH=src $(PYTHON_TRAIN) -m treinamento_visual.ingest

prepare-tasks:
	PYTHONPATH=src $(PYTHON_APP) -m treinamento_visual.label.cli preparar

label-studio:
	PYTHONPATH=src $(PYTHON_TRAIN) -m treinamento_visual.label.cli start --port 8080

build-dataset:
	PYTHONPATH=src $(PYTHON_APP) -m treinamento_visual.train.build_dataset

check-dataset:
	PYTHONPATH=src $(PYTHON_APP) -m treinamento_visual.train.check_dataset --modelo models/base-smol

export-dataset:
	PUBLICAR_DATASET=1 PYTHONPATH=src $(PYTHON_APP) \
		-m treinamento_visual.train.export_public_dataset

train-mac:
	$(CURDIR)/.venv-treinamento/bin/mlx_vlm.train \
		--task vlm --algorithm sft \
		--model models/base-smol \
		--data data/treinamento/dataset \
		--train-split train --validation-split valid \
		--train-type lora --lora-rank 8 --lora-alpha 16 \
		--batch-size 1 --max-seq-length 2048 --iters 8 \
		--steps-per-report 1 --steps-per-eval 2 --steps-per-save 4 \
		--output-path models/adapters/smolvlm-melhorado/adapters.safetensors \
		--grad-checkpoint --no-compile --max-memory-gb 8 --max-minutes 10

train-ci:
	PYTHONPATH=src $(PYTHON_APP) -m treinamento_visual.train.train_huggingface --dry-run

convert:
	bash src/treinamento_visual/scripts/converter_modelo_smolvlm.sh

build-extension:
	bash src/treinamento_visual/scripts/build_extension.sh

clean:
	find src tests -type f -name '*.pyc' -delete
	find src tests -type d -name '__pycache__' -empty -delete
	rm -rf build
