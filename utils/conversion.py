import argparse
import re
#from bs4 import BeautifulSoup


table_of_conversion={
    "<|eot_id|>": "",
    "<|begin_of_svg|>": "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n<svg viewBox=\"0  0 512  512\" version=\"1.1\" xmlns=\"http://www.w3.org/2000/svg\">\n",
    "<|end_of_svg|>": "</svg>",
    "<|begin_of_style|>": "<path style=\"",
    "<|begin_of_path|>": "d=\"",
    "<|end_of_path|>": "Z\"/>\n",
    "<|end_of_style|>": "\"\t", # to adjust
    "<|M|>": " M",
    "<|L|>": " L",
    "<|C|>": " C",
    "<|A|>": " A",
    "<|currentColor|>": "currentColor",
    "<|color|>": "fill:",
    "<|stroke-width|>": ";stroke-width:",
    "<|stroke|>": ";stroke:",
    "<|opacity|>": ";opacity:",
    "<|SEP|>": ",",
    "<|none|>": "none"
}

def replacer(match):
    if "stroke" in match.group(0):
        new_s = match.group(0).replace("stroke:","stroke:rgb(") + ")"
    elif "fill" in match.group(0):
        new_s = match.group(0).replace("fill:","fill:rgb(") + ")"
    return new_s

def parse_args():
    parser = argparse.ArgumentParser(description='Convert a prediction to a svg file')
    parser.add_argument('--file', type=str)
    args = parser.parse_args()
    return args


def clean_lastline_svg(svg):
    if "</svg>" in svg:
        svg = svg.split('</svg>')[0].rsplit('/>',1)[0] + '/></svg>'
    else:
        svg = "\n".join(svg.split('\n')[:-1])+"\n</svg>"

    return svg



def from_prediction(predictions):
    # Gestire <|eot_id|>
    if type(predictions) == str:
        predictions = [predictions] 
    for i in range(len(predictions)):
        predictions[i] = "<|begin_of_svg|>" + predictions[i][predictions[i].find("<|begin_of_style|>"):]
        for token, value in table_of_conversion.items():
            predictions[i] = predictions[i].replace(token,value) 
        predictions[i] = re.sub("stroke:([0-9]{1,3},?){3}", replacer, predictions[i])
        predictions[i] = re.sub("fill:([0-9]{1,3},?){3}", replacer, predictions[i])
        predictions[i] = clean_lastline_svg(predictions[i])
    if len(predictions) == 1:
        return predictions[0]
    return predictions


def main(file):
    with open(file) as f:
        pred = f.read()
    pred = pred.split('### SVG: ')[1]
    with open(file+'.svg','w') as f:
        f.write(from_prediction(pred))
    
if __name__ == '__main__':
    main(parse_args().file)