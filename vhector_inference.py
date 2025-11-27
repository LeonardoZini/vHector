import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from utils.conversion import from_prediction


model = AutoModelForCausalLM.from_pretrained("lzini/vHector-8B", local_files_only=True).to('cuda').eval()
tokenizer = AutoTokenizer.from_pretrained("lzini/vHector-8B", local_files_only=True)

tokenizer.eos_token_id = tokenizer.convert_tokens_to_ids('<|end_of_svg|>')
tokenizer.pad_token_id = tokenizer.eos_token_id

prompt = "The image depicts an icon of a monitor."
text = f"### ImageDescription: {prompt}.\n ### SVG: <|begin_of_svg|><|begin_of_style|>"

input_ids = tokenizer(text, padding=True, padding_side="left", return_tensors="pt").to(torch.device("cuda"))

with torch.no_grad():
    #res = model.generate(**input_ids, max_length=8300)
    res = model.generate(**input_ids, max_length=8300, temperature=0.2, eos_token_id=tokenizer.eos_token_id)

out = []
for r in res:
    output_svg = from_prediction(tokenizer.decode(r)).split("</svg>")[0] + "</svg>"
