import json
import os
import re
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description='Clean color in SVGs')
    parser.add_argument('--file', type=str)
    args = parser.parse_args()
    return args


with open('svg_parser/svg_utils/color_tab.json','r') as f:
    color_tab = json.load(f)

def triplet_from_str(color_str):
    color_str = '#' + color_str
    if "url" in color_str:
        return f"{int('0xFF',16)},{int('0xFF',16)},{int('0xFF',16)}"


    starts = color_str.split('#')[1]
    if len(starts) == 6:
        red = int('0x' + starts[:2],16)
        green = int('0x' + starts[2:4],16)
        blue = int('0x' + starts[4:],16)
    elif len(starts) == 3:
        red = int('0x' + starts[0]*2,16)
        green = int('0x' + starts[1]*2,16)
        blue = int('0x' + starts[2]*2,16)
    else:
        while len(starts) < 6:
            starts += starts[-1]
        red = int('0x' + starts[:2],16)
        green = int('0x' + starts[2:4],16)
        blue = int('0x' + starts[4:],16)       

    
    return f"{red},{green},{blue}"



def replace_url(s):
    for col in re.findall(r'url\((.+)\)',s):
        s = s.replace(f"url({col})", 'None')
    return s

def replace_rgb(s):


    for col in re.findall(r'#([0-9a-fA-F]{3,6})',s):
        s = s.replace(f'#{col}', f"rgb({triplet_from_str(col)})")

    for col in re.findall(r'rgb\(([^\)]+)\);',s):
        try:
            r,g,b = [x.strip('%').strip() for x in col.split(',')]
        except Exception:
            print(col)
            print([x for x in col.split(',')])
            print('ERROR in parsing a color')
        new_col = f"{r},{g},{b}"
        s = s.replace(f'rgb({col})', f'rgb({new_col})')
    return s

def replace_color(s):
    for c in color_tab:
        s = s.replace(c,f"rgb({triplet_from_str(color_tab[c.lower()])})")
    return s
        
def round_stroke_and_op(s):
    for col in re.findall(r'stroke-width:(\d*\.\d+)',s):
        s = s.replace(f'stroke-width:{col}', f'stroke-width:{round(float(col),2)}')
    for col in re.findall(r'opacity:(\d+\.\d+)',s):
        s = s.replace(f'opacity:{col}', f'opacity:{round(float(col),2)}')
    return s

def clean_hex(s):
    for col in re.findall(r'(fill|stroke)\:([0-9a-fA-F]{6})',s):
        s = s.replace(f'{col[1]}', f"rgb({triplet_from_str(col[1])})")
        print(col)
    return s

def clean_broken_triplets(s):
    for col in re.findall(r'(fill|stroke)\:(255,255,255[^;]+)',s):
        s = s.replace(f'{col[0]}:{col[1]}', f'{col[0]}:rgb({"".join([x*2 for x in col[1][11:]])})')
    return s

def clean_color(svg):

    
    svg = replace_url(svg)
    svg = clean_hex(svg)
    svg = clean_broken_triplets(svg)
    svg = replace_color(svg)  
    svg = round_stroke_and_op(svg)
    svg = replace_rgb(svg)
    return svg



if __name__ == '__main__':
    args = parse_args()
    print()
    clean_color(args.file,args.file)