import xml.etree.ElementTree as ET

from .svg_utils.Path import *
from .svg_utils import parsing





def triplet_from_str(color_str):
    
    
    if "url" in color_str or '#' not in color_str:
        return int('0xFF',16), int('0xFF',16), int('0xFF',16)

    try:

        starts = color_str.split('#')[1]
        if len(starts) == 6:
            red = int('0x' + starts[:2],16)
            green = int('0x' + starts[2:4],16)
            blue = int('0x' + starts[4:],16)
        elif len(starts) == 3:
            red = int('0x' + starts[0]*2,16)
            green = int('0x' + starts[1]*2,16)
            blue = int('0x' + starts[2]*2,16)

    except Exception:
        print(starts)
        print('ERROR in parsing a color')
        return None
    
    return (red,green,blue)



class Parser:
    def __init__(self, filename, ns={'svg': 'http://www.w3.org/2000/svg'}, maintain_aspect_ratio=False):
        tree = ET.parse(filename)
        self.root = tree.getroot()
        self.ns = ns
        self.viewBox = self.root.get('viewBox')
        if self.viewBox is None:
            height, width = self.root.get('height'), self.root.get('width')
            self.viewBox = f"0 0 {width} {height}"
            assert (height is not None and width is not None)
        
        
        try:
            self.svg = SVG(tuple(map(lambda x: round(float(x)), re.findall(r'([0-9\.]+)[,|\s]?',self.viewBox))), maintain_aspect_ratio=maintain_aspect_ratio)
            

        except ValueError:
            values = []
            for v in  self.viewBox.split(' '):
                if 'px' in v:
                    values.append(v.split('px')[0].split('.')[0])
                elif 'pt' in v:
                    values.append(v.split('pt')[0].split('.')[0])
                else:
                    values.append(v.split('.')[0])
                
            self.svg = SVG(tuple(map(int, values)), maintain_aspect_ratio=maintain_aspect_ratio)    
            
        self.common_style = {}
        self.original_size = self.svg.viewBox[2:]

    def extract_elements(self, group=None, style=None, transform=None):
        if group is None:
            group=self.root
            style_tmp = parsing.parse_style(self.root)
            if style_tmp != tuple([None]*4):
                style.append(style_tmp)

        groups = group.iterfind('*')
        for child in groups:

            if child.tag == "{"+self.ns['svg']+"}g":

                #style = parse_style(child)
                style_tmp = parse_style(child)
                if style_tmp != tuple([None]*4):
                    style.append(style_tmp)
                    

                transform_tmp = child.get('transform')
                if transform_tmp != None:
                    transform.append(transform_tmp)
                
                self.extract_elements(child, style=style, transform=transform)
                if transform_tmp != None:
                    transform = transform[:-1]
                
                if style_tmp != tuple([None]*4):
                    style.remove(style_tmp)

            else:
                

                if child.tag.endswith('rect'):
                    rect_et = Rectangle(self.common_style, self.original_size)
                    rect_et.extract_from_ET(child)

                    if style != []:

                        rect_et.force_style(style[-1])
                    if transform != []:
                        rect_et.apply_transform(transform)
                    self.svg.add(rect_et)

                    
                    
                elif child.tag.endswith('polygon'):
                    poly_et = Polygon(self.common_style)
                    poly_et.extract_from_ET(child)
                    if style != []:

                        poly_et.force_style(style[-1])
                    if transform != []:
                        poly_et.apply_transform(transform)
                    self.svg.add(poly_et)
                    

                elif child.tag.endswith('circle'):
                    circle_et = Circle(self.common_style)
                    circle_et.extract_from_ET(child)
                    if style != []:
                        circle_et.force_style(style[-1])
                    if transform != []:
                        circle_et.apply_transform(transform)
                    self.svg.add(circle_et)

                elif child.tag.endswith('ellipse'):
                    ellipse_et = Ellipse(self.common_style)
                    ellipse_et.extract_from_ET(child)
                    if style != []:
                        ellipse_et.force_style(style[-1])

                    if transform != []:
                        ellipse_et.apply_transform(transform)
                    self.svg.add(ellipse_et)


                elif child.tag.endswith('path'):
                    path_et = PathSVG(self.common_style)
                    path_et.extract_from_ET(child)
                    if style != []:
                        path_et.force_style(style[-1])
                    
                    if transform != []:
                        path_et.apply_transform(transform)
                    self.svg.add(path_et)

                elif child.tag.endswith('}polyline'):
                    
                    polyline_et = Polyline(self.common_style)
                    polyline_et.extract_from_ET(child)
                    if style != []:

                        polyline_et.force_style(style[-1])
                    if transform != []:
                        polyline_et.apply_transform(transform)
                    self.svg.add(polyline_et)
                
                elif child.tag.endswith('}line'):
                    line_et = Line(self.common_style)
                    line_et.extract_from_ET(child)
                    if style != []:
                        line_et.force_style(style[-1])
                    if transform != []:
                        line_et.apply_transform(transform)
                    self.svg.add(line_et)
                
                

   

    def parse(self):


        css_dict = parse_css_styles(self.root)
        css_dict = {} if css_dict is None else css_dict
        dict_gradients = parse_gradients(self.root)
        dict_gradients = {} if dict_gradients is None else dict_gradients 
        
        self.common_style = {**css_dict, **dict_gradients}
        
        self.extract_elements(style=[], transform=[])
    
    def get(self):
        return self.svg.svg
    
    def to_string(self):
        out = "<|begin_of_svg|>"
        for path in self.get():
            out += "<|begin_of_path|>"
            out+="<|start_of_style|>"
            if path.specs['color'] == 'none':
                out += '<|color|><|none|>'
            elif path.specs['color'] is not None:
                    rgb = triplet_from_str(path.specs['color'])
                
                    out+= '<|color|>'
                    out+= '<|NUM|>'
                    out+= str(round(rgb[0]))
                    out+= '<|NUM|>'
                    out+= str(round(rgb[1]))
                    out+= '<|NUM|>'
                    out+= str(round(rgb[2]))
                
            if path.specs['stroke'] is not None:
                r,g,b = triplet_from_str(path.specs['stroke'])
                out+= '<|stroke|>'
                out+= '<|NUM|>'
                out+= str(round(r))
                out+= '<|NUM|>'
                out+= str(round(g))
                out+= '<|NUM|>'
                out+= str(round(b))

            if path.specs['opacity'] is not None:
                out += '<|opacity|>'
                out += '<|NUM|>'
                out += str(round(float(path.specs['opacity'])*10))
            out+="<|end_of_style|>"
            out+="<|start_of_commands|>"
            for command, points in path.specs['path']:
                out += f"<|{command}|>"
                for point in points:
                    out += '<|NUM|>'
                    out += str(round(point))
            out+="<|end_of_commands|>"
            out += "<|end_of_path|>"
        out += "<|end_of_svg|>"
        return out
