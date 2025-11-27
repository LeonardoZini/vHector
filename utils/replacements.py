def token_texts():
    convert_text = {
        '<|begin_of_svg|>': '<|begin_of_svg|>',
        '<|end_of_svg|>': '<|end_of_svg|>',
        '<path style=\"': '<|begin_of_style|>',
        'd=\"M': '<|begin_of_path|><|M|>',
        ' M': '<|M|>',
        ' L': '<|L|>',  
        ' C': '<|C|>',
        ' A': '<|A|>',
        'fill:': '<|color|>',
        'stroke-width:': '<|stroke-width|>',
        'stroke:': '<|stroke|>',
        'opacity:': '<|opacity|>',
        '\"\t': '<|end_of_style|>',
        ',': '<|SEP|>',
        'none': '<|none|>',
        'None': '<|none|>',
        ' \" />\n': '<|end_of_path|>',
        'currentColor': '<|currentColor|>',
        ';': '',
        'rgb(': '',
        ')': ''
    }
    tmp = list(convert_text.values())
    tmp.remove('')
    return tmp, convert_text

new_tokens = {
    'text': token_texts()
}

new_token_list = ['<|begin_of_svg|>', '<|end_of_svg|>', '<|begin_of_style|>', '<|end_of_style|>', '<|begin_of_path|>', '<|end_of_path|>', '<|M|>', '<|L|>', '<|C|>', '<|A|>', '<|color|>', '<|stroke-width|>', '<|stroke|>', '<|opacity|>', '<|none|>', '<|currentColor|>', '<|SEP|>']


def pretokenize_svg(svg, sep=False):
    svg = "\n".join(svg.split('\n')[3:-1])+'\n'
    _, convert_text = new_tokens['text']
    for token, value in convert_text.items():
        svg = svg.replace(token,value)
    svg = f"<|begin_of_svg|>{svg}<|end_of_svg|>"
    

    
    return svg