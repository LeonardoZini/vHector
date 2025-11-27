# vHector and HeisenVec

[![Paper](https://img.shields.io/badge/Paper-OpenReview-blue)](https://openreview.net/pdf?id=diYaFg8pqm)

Official code repository for **vHector and HeisenVec: Scalable Vector Graphics Generation Through Large Language Models**.

This repository provides a complete toolkit for SVG generation using Large Language Models, including:
- The **vHector model** for text-to-SVG generation
- The **HeisenVec dataset** preprocessing and parsing tools
- Inference and evaluation utilities

## 📰 News

🎉 **November 2025**: Our paper has been accepted at **NeurIPS 2025** (Datasets and Benchmarks Track)!

📄 **Paper**: [Read on OpenReview](https://openreview.net/pdf?id=diYaFg8pqm)

## 🗃️ Dataset

The **HeisenVec dataset** is available on Hugging Face: [aimagelab/HeisenVec](https://huggingface.co/datasets/aimagelab/HeisenVec)

## 🖼️ Qualitative Results

### Parser Standardization Quality

Our SVG standardization parser introduces minimal error, if any, as shown in the comparison below:

[View Parser Comparison (PDF)](images/sup_parsing_comparison.pdf)

The comparison demonstrates that the standardization process preserves visual fidelity while normalizing the SVG structure.

### vHector Generation Results

Qualitative comparison of vHector against competing methods:

[View vHector Qualitative Results](images/vHector_demo_qualitatives.png)

The results showcase vHector's superior generation quality from text descriptions compared to baseline approaches.

## 🔧 Features

- **SVG Standardization**: Cleans styles, normalizes colors (translating triplets from base16 to base10), removes redundant commands, and flattens structure.
- **Custom Tokenizer Extension**: Adds SVG-specific tokens to any Hugging Face tokenizer.
- **Text-to-SVG Generation**: Generate vector graphics from natural language descriptions using the vHector model.
- **Tokenization & De-Tokenization** (for debugging purposes): Converts SVG to token sequences and reconstructs the original vector image.
- **Outputs at Each Stage** (for debugging purposes): Saves intermediate steps for full traceability and debugging.

## 📦 Installation

TODO: Add installation instructions for the environment.

## 🗂 Directory Structure

```bash
vHector/
│
├── svg_parser/
│   ├── Parser.py
│   └── svg_utils/
│       ├── parsing.py
│       ├── Path.py
│       └── color_tab.json
│
├── utils/
│   ├── clean_color.py
│   ├── clean_commands.py
│   ├── replacements.py
│   └── conversion.py
│
├── outputs/
│   ├── replaced.txt             # SVG string with token replacements
│   └── tokenized.json           # Token IDs and strings
│
├── svg_parsing.py               # SVG parsing and preprocessing
└── vhector_inference.py         # vHector model inference
``` 

## 🎨 SVG Parsing Guide

The parsing pipeline standardizes SVG files for training and evaluation. It performs cleaning, normalization, tokenization, and reconstruction.

### Usage

```bash 
python svg_parsing.py --img path/to/your/input.svg
```

### Pipeline Components

| Step | Function | Description |
| --- | --- | --- |
| `standardization()` | Parses and cleans SVG | Normalizes format, colors, and removes redundancies |
| `replacement()` | Applies custom tokens | Shortens repetitive SVG patterns using `new_token_list` |
| `build_tokenizer()` | Loads and extends tokenizer | Adds special tokens for SVG to a Hugging Face tokenizer |
| `tokenization()` | Tokenizes input | Converts preprocessed SVG string into token IDs |
| `reconstruction()` | From tokens to SVG | Reconstructs SVG from model predictions using decoding and post-processing |

### Outputs

After execution, the following files are generated in the `outputs/` directory:

- **replaced.txt**: SVG with pretokenization replacements.
- **tokenized.json**: Token IDs and their corresponding token strings.

## 🚀 Inference Guide

Generate SVG images from text descriptions using the vHector model.


### Command Line Interface 

Future versions will support command-line text input:

```bash
python vhector_inference.py --prompt "The image depicts an icon of a monitor." --model_name lzini/vHector-8B
```

### Important Notes

- All prompts **must begin with "The image depicts"** for optimal generation quality.
- The model is trained on this specific prompt format.
- Maximum sequence length is 8192 tokens.
- Temperature can be adjusted (default: 0.2) for more diverse outputs.

## 📄 Citation

If you use this code or the vHector model in your research, please cite our paper:

```bibtex
@inproceedings{
zini2025vhector,
title={vHector and HeisenVec: Scalable Vector Graphics Generation Through Large Language Models},
author={Leonardo Zini and Elia Frigieri and Sebastiano Aloscari and Lorenzo Baraldi},
booktitle={The Thirty-ninth Annual Conference on Neural Information Processing Systems Datasets and Benchmarks Track},
year={2025},
url={https://openreview.net/forum?id=diYaFg8pqm}
}
```


