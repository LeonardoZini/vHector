import xml.etree.ElementTree as ET
import re
import json

color_tab_filename='svg_parser/svg_utils/color_tab.json'
with open(color_tab_filename,'r') as f:
    svg_colors = json.loads(f.read())



def convert_circle_to_path(cx, cy, r):
    path_data = f"M{cx - r},{cy} "
    path_data += f"A{r},{r} 0 1,0 {cx + r},{cy} "
    path_data += f"A{r},{r} 0 1,0 {cx - r},{cy} "
    path_data += "Z"

    return path_data

def convert_rect_to_path(x, y, width, height, rx=0, ry=0):
    if rx == 0 and ry > 0:
        rx = ry
    elif ry == 0 and rx > 0:
        ry = rx
    
    path_data = f"M{x+rx},{y} "  
    path_data += f"L{x + width-rx},{y} " 
    
    if rx != 0 or ry != 0: 
        path_data += f"A{rx},{ry} 0 0 1 {x + width}, {y+ry} "  

    path_data += f"L{x + width},{y + height - ry} "
    
    if rx != 0 or ry != 0: 
        path_data += f"A{rx},{ry} 0 0 1 {x + width - rx}, {y+height} "  

    path_data += f"L{x+rx},{y + height} "
    
    if rx != 0 or ry != 0: 
        path_data += f"A{rx},{ry} 0 0 1 {x}, {y+height-ry} "  

    path_data += f"L{x},{y + ry} "
    
    if rx != 0 or ry != 0: 
        path_data += f"A{rx},{ry} 0 0 1 {x+rx}, {y} "

    path_data += "Z"  
    
    return path_data


def convert_line_to_path(x1,y1,x2,y2):
    path_data = f"M {x1} {y1}"
    path_data += f"L {x2} {y2}"
    path_data += " Z"

    return path_data

def convert_poly_to_path(polyline_points, polygon=True):
    points = [] 
    for i in re.finditer(r'([0-9\.]+)[\s|,]?', polyline_points):
        points.append(i.group(0).strip(','))

    if points == []:
        raise Exception("Error: void points list")

    path_data = f"M {points[0]} {points[1]}"

    for point_x, point_y in zip(points[2::2], points[3::2]):
        path_data += f" L {point_x} {point_y}"

    if polygon:
        path_data += f"L {points[0]} {points[1]}"
    path_data += " Z"

    return path_data

def convert_ellipse_to_path(cx,cy,rx,ry):
    path_data = f"M {(cx - rx)}, {cy} \
    A {rx}, {ry} 0 1,0 {(cx + rx)}, {cy} \
    A {rx}, {ry} 0 1,0 {(cx - rx)}, {cy} Z"
    return path_data


def parse_style(style):
        fill = opacity = stroke = stroke_width = None
        if style.get('style') is None: 
            fill = style.get('fill')
            opacity = style.get('opacity')      
            stroke = style.get('stroke')
            if stroke == 'none':
                stroke = None
            stroke_width = style.get('stroke-width')
            if stroke_width is not None:
                if 'px' in stroke_width:
                    stroke_width = stroke_width.split('px')[0]


        else:
            style = style.get('style')
            for st in style.split(';'):
                if st.startswith('fill:'):
                    fill = st.split(':')[1]

                elif st.startswith('opacity:'):
                    opacity = st.split(':')[1]

                elif st.startswith('stroke:'):
                    stroke = st.split(':')[1]
                    if stroke == 'none':
                        stroke = None
                
                elif st.startswith('stroke-width:'):
                    stroke_width = st.split(':')[1]
                    if stroke_width == 'none':
                        stroke_width = None
                    if stroke_width is not None:
                        if 'px' in stroke_width:
                            stroke_width = stroke_width.split('px')[0]
        
    
        if fill in svg_colors.keys():
            fill = '#' + svg_colors[fill]
        

        if stroke in svg_colors.keys():
            stroke = '#' + svg_colors[stroke]

        return (fill, opacity, stroke, stroke_width)


# Function to parse the transform string
def parse_transform(transform_str):
    # Regular expression to match different transformation types and their arguments
    transform_regex = re.compile(
        r'(translate|rotate|scale|skewX|skewY|matrix)\s*\(([^)]+)\)'
    )
    
    # List to store transformations in the order they appear
    transformations = []
    
    # Iterate over all matches in the transform string
    for match in transform_regex.finditer(transform_str):
        transform_type = match.group(1)
        params_str = match.group(2)
        
        # Convert parameters to a list of floats
        params = list(map(float, re.split(r'[ ,]+', params_str.strip())))
        
        # Append the transformation type and its parameters as a tuple
        transformations.append((transform_type, params))

    return transformations


def parse_gradients(root):
        lGs = root.findall('.//{http://www.w3.org/2000/svg}linearGradient')
        rGs = root.findall('.//{http://www.w3.org/2000/svg}radialGradient')
        styles_dict = dict()
        for g in lGs+rGs:
            id = g.get('id').strip()
            stop = g.findall('{http://www.w3.org/2000/svg}stop')
            if stop == []:
                href = g.get('{http://www.w3.org/1999/xlink}href')
                if href != None:
                    if href.strip('#') not in styles_dict.keys():
                        continue
                    styles_dict[id] = dict()
                    styles_dict[id]['fill'] = styles_dict[href.strip('#')]['fill']
                continue
            stop = stop[-1]
            
            if stop.get('style') is not None:
                for attr in stop.get('style').split(';'):
                    if attr.startswith('stop-color'):
                        color = attr.split(':')[1]
                        assert id not in styles_dict.keys()
                        styles_dict[id] = dict()
                        styles_dict[id]['fill'] = color.strip('}')
            elif stop.get('stop-color') is not None:
                color = stop.get('stop-color')
                assert id not in styles_dict.keys()
                styles_dict[id] = dict()
                styles_dict[id]['fill'] = color.strip('}')
            else:
                styles_dict[id] = dict()
                styles_dict[id]['fill'] = "#FFFFFF"
                
                
        
        return styles_dict

def parse_css_styles(root):
        defs = root.find('{http://www.w3.org/2000/svg}defs')
        style_def = None
        
        if defs is not None:
            style_def = defs.find('{http://www.w3.org/2000/svg}style')
        
        style_main = root.find('{http://www.w3.org/2000/svg}style')
        
        styles = None
        if style_def is not None and style_def.text is not None:
            style_str = style_def.text
            styles = style_str.split('.')[1:]
            
        elif style_main is not None and style_main.text is not None:
            styles = style_main.text.split('.')[1:]

        styles_dict = {}
        if styles is None:
            return
        
        for style in styles:
            style=style.strip()
            out = style.split('{')
            if len(out)==2:
                id,st = out
                id = id.strip()
                if id not in styles_dict.keys():
                    styles_dict[id] = dict()
                for s in st.split(';'):
                    if s.strip() != '}' and '/*' not in s:
                        command, arg = s.split(':')
                        styles_dict[id][command] = arg.strip('}')
                        
        return styles_dict
    

