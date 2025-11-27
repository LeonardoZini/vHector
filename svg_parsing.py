from svg_parser.Parser import Parser
import argparse
from utils.clean_color import clean_color
from utils.replacements import pretokenize_svg, new_tokens, new_token_list
from utils.clean_commands import clean_repetitive_commands
import warnings
from transformers import AutoTokenizer, AutoModelForCausalLM
import json
from utils.conversion import from_prediction




def standardization(filename):
    parser = Parser(filename)
    parser.parse()

    s = str(parser.svg)
    s = clean_color(s)
    s = clean_repetitive_commands(s)
    return s

def replacement(s):
    return pretokenize_svg(s)

def tokenization(s, tokenizer):
    token_list = tokenizer.tokenize(s)
    s = tokenizer(s)['input_ids']
    return s[1:], token_list

def reconstruction(svg_tokens, tokenizer):
    s = tokenizer.decode(svg_tokens, skip_special_tokens=True)
    s = from_prediction(s)
    return s


def build_tokenizer(model_name):
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    tokenizer.add_tokens(new_tokens=new_token_list)
     

    tokenizer.pad_token = tokenizer.eos_token
    tokenizer.pad_token_id = tokenizer.eos_token_id
    tokenizer.padding_side = "right" 
    
    
    if '<pad>' not in tokenizer.get_vocab():
        tokenizer.add_special_tokens({"pad_token":"<pad>"})

    return tokenizer

def parse_args():
    parser = argparse.ArgumentParser(description='SVG Parser and tokenization')
    parser.add_argument('--img', type=str, default="example.svg")

    args = parser.parse_args()
    return args


def main(args):

    # Parse the SVG file following the paper, translating color in the format rgb(r,g,b) 
    # clean consecutive repetitive commmands
    # and remove the unnecessary spaces
    svg = standardization(args.img)
    
    with open('outputs/standardized.svg','w+') as f:
        f.write(svg)
    
    # Replace the substrings in the SVG file with the new tokens
    svg = replacement(svg)

    with open('outputs/replaced.txt','w+') as f:
        f.write(svg)

    model_name = "meta-llama/Llama-3.1-8B-Instruct"
    tokenizer = build_tokenizer(model_name)

    # Tokenize the SVG file using the added tokens demonstrating compression
    svg, svg_tokens = tokenization(svg, tokenizer)
    res = [(svg[i], svg_tokens[i]) for i in range(len(svg))]


    with open('outputs/tokenized.json','w+') as f:
        json.dump(res, f, indent=4)

    # Reconstruct the SVG file from the tokenized version, a.k.a. the prediction
    svg = reconstruction(svg, tokenizer)
    
    with open('outputs/reconstructed.svg','w+') as f:
        f.write(svg)

if __name__ == '__main__':
    args = parse_args()
    main(args)