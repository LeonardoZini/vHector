import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from utils.conversion import from_prediction
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description='vHector Inference')
    parser.add_argument('--prompt', type=str, required=True, help='Text prompt describing the desired SVG image')
    parser.add_argument('--model_name', type=str, default="lzini/vHector-8B", help='Pretrained model name or path')
    parser.add_argument('--output_file', type=str, default="output_generation.svg", help='File to save the generated SVG image')
    args = parser.parse_args()
    return args

def main(args):
    args = parse_args()

    model = AutoModelForCausalLM.from_pretrained(args.model_name, local_files_only=True).to('cuda').eval()
    tokenizer = AutoTokenizer.from_pretrained(args.model_name, local_files_only=True)

    tokenizer.eos_token_id = tokenizer.convert_tokens_to_ids('<|end_of_svg|>')
    tokenizer.pad_token_id = tokenizer.eos_token_id

    prompt = args.prompt
    if not prompt.startswith('The image depicts '):
        prompt = "The image depicts " + prompt
    text = f"### ImageDescription: {prompt}.\n ### SVG: <|begin_of_svg|><|begin_of_style|>"

    input_ids = tokenizer(text, padding=True, padding_side="left", return_tensors="pt").to(torch.device("cuda"))

    with torch.no_grad():
        res = model.generate(**input_ids, max_length=8192, temperature=0.2, eos_token_id=tokenizer.eos_token_id)

    
    output_svg = from_prediction(tokenizer.decode(res[0])).split("</svg>")[0] + "</svg>"
    with open(args.output_file, "w") as f:
        f.write(output_svg)
    
    print(f"SVG image saved to {args.output_file}")


if __name__ == "__main__":
    args = parse_args()
    main(args)