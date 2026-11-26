---
base_model:
- HuggingFaceTB/SmolVLM-Instruct
datasets:
- HuggingFaceM4/the_cauldron
- HuggingFaceM4/Docmatix
language:
- en
library_name: transformers
license: apache-2.0
pipeline_tag: image-text-to-text
tags:
- mlx
---

# mlx-community/SmolVLM-Instruct-4bit
This model was converted to MLX format from [`HuggingFaceTB/SmolVLM-Instruct`]() using mlx-vlm version **0.1.2**.
Refer to the [original model card](https://huggingface.co/HuggingFaceTB/SmolVLM-Instruct) for more details on the model.
## Use with mlx

```bash
pip install -U mlx-vlm
```

```bash
python -m mlx_vlm.generate --model mlx-community/SmolVLM-Instruct-4bit --max-tokens 100 --temp 0.0
```
