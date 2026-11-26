# Vocabulário do projeto

## Tipos de modelo

- **GPT-6 Luna:** modelo remoto configurado para intenção, revisão textual e síntese.
- **SmolVLM:** modelo leve de visão para analisar imagens de documentos.
- **LoRA/Adaptador:** ajuste pequeno aplicado sobre um modelo base.
- **Base model:** modelo completo original usado antes de um adaptador.

## Formatos

- **JSON:** dados estruturados usados pelo projeto e pelos prompts.
- **JSONL:** uma linha JSON por exemplo em datasets de treino.
- **GGUF:** arquivo compacto de modelo executado pelo llama.cpp.
- **mmproj:** componente GGUF que permite ao modelo receber imagens.
- **Safetensors:** formato seguro para armazenar pesos de modelos.

## Ferramentas

- **PyMuPDF:** abre PDFs e renderiza páginas em imagens.
- **Tesseract/Pytesseract:** OCR que transforma imagem em texto auxiliar.
- **Label Studio:** interface para desenhar caixas e transcrever campos.
- **Transformers:** biblioteca Hugging Face para carregar e treinar modelos.
- **PEFT:** biblioteca que cria e aplica LoRA/PEFT.
- **MLX:** infraestrutura da Apple para treino local em Mac.
- **llama.cpp:** servidor local rápido para modelos GGUF.
- **Streamlit:** interface web em Python.
- **OpenAI SDK:** comunicação com API compatível com GPT-6 Luna.
- **Requests:** chamadas HTTP ao servidor local ou APIs.
- **Sentry:** ferramenta de monitoramento e telemetria. Neste projeto ela é
  desativada no Label Studio local por privacidade.
- **Make:** executor simples de tarefas, usando o Makefile.
- **Dev Container/Codespaces:** ambiente Linux reproduzível para o projeto.

## Nomenclatura visual

- **Label:** caixa da região e sua transcrição no documento.
- **Dataset:** imagens, instruções e respostas revisadas usadas no treino.
- **Teste reservado:** documentos separados do treino usados para medir
  generalização.
- **Aprovação:** decisão humana de ativar um adaptador após avaliação.
