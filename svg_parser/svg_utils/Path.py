import re
from .parsing import *
import math
import svgpathtools

def rgb_to_hex(rgb):
    rgb = rgb.strip().strip('rgb(').strip(')').split(',')
    return '#%02x%02x%02x' % (int(rgb[0].strip('%').strip('px')), int(rgb[1].strip('%').strip('px')), int(rgb[2].strip('%').strip('px')))
    
class PathSVG:


    def __init__(self, style = None):
        
        self.specs = {
            "color" : '#000000',
            "opacity" : 1,
            "stroke"  : None,
            "stroke-width": 1,
            "path" : []
        }
        if style == None:
            style=dict()

        self.styles = style
    
 

    # Common to each subclass    
    def set_color_from_et(self,el_svg):
    
        # rimuovere rgb da qua
        class_style = el_svg.get('class')
        if class_style is None:
            fill, opacity, stroke, stroke_width = parse_style(el_svg) 

            if opacity is not None:
                self.specs['opacity'] = opacity
            
            if fill is not None:
                if 'url' in fill:
                    key = fill.split('url(#')[1].strip(')')
                    if key in self.styles.keys():
                        fill = self.styles[key]['fill']
                    else:
                        #print(f"Color not find: {key} in {self.styles.keys()}")
                        pass
                
                if 'rgb' in fill:
                    fill = rgb_to_hex(fill)
                self.specs['color'] = fill
            
            if stroke is not None:
                if stroke == 'currentColor':
                    stroke=fill

                if 'rgb' in stroke:
                    stroke = rgb_to_hex(stroke)
                self.specs['stroke'] = stroke
            
            if stroke_width is not None:
                self.specs['stroke-width'] = stroke_width

        else:
            for cls_style in class_style.split(' '):
                if cls_style in self.styles.keys():
                    for k,v in self.styles[cls_style].items():
                        if k == 'fill':
                            k='color'
                        self.specs[k] = v


    def path_from_str(self,path_str):
        # This function returns  absolute path command (uppercase letter) and removes arcs
        
        last_end = complex()
        try:
            elms = svgpathtools.parse_path(path_str)

            if type(self) == Polyline:
                elms=elms[:-1]
            if elms != svgpathtools.Path():
                self.specs['path'].append(('M',[elms[0].start.real, elms[0].start.imag]))
                last_end = complex(elms[0].start.real, elms[0].start.imag)
            else:
                points = re.findall(r'(?i)M([0-9\.]+)[,\s]([0-9\.]+)', path_str)
                if len(points) >= 1:
                    self.specs['path'].append(('M',[float(points[0][0]), float(points[0][1])]))
                    last_end = complex(float(points[-1][0]), float(points[-1][1]))

            for segment in elms:
                if segment.start != last_end:
                    self.specs['path'].append(('M',[segment.start.real, segment.start.imag]))
                if isinstance(segment, svgpathtools.Arc):


                    numbers = [segment.radius.real, segment.radius.imag, segment.rotation, 1 if segment.large_arc else 0, 1 if segment.sweep else 0, segment.end.real, segment.end.imag]
                    self.specs['path'].append(('A',numbers))


                elif isinstance(segment, svgpathtools.QuadraticBezier):
                    # Convert the quadratic bezier to cubic Bézier curves
                    c1_x = segment.start.real + (2/3) * (segment.control.real - segment.start.real)
                    c1_y = segment.start.imag + (2/3) * (segment.control.imag - segment.start.imag)

                    c2_x = segment.end.real + (2/3) * (segment.control.real - segment.end.real)
                    c2_y = segment.end.imag + (2/3) * (segment.control.imag - segment.end.imag) 
                    res = svgpathtools.CubicBezier(segment.start,complex(c1_x, c1_y),complex(c2_x, c2_y),segment.end)

                    numbers = [res.control1.real, res.control1.imag, res.control2.real, res.control2.imag, res.end.real, res.end.imag]
                    self.specs['path'].append(('C',numbers))

                elif isinstance(segment, svgpathtools.Line):
                    numbers = [segment.end.real, segment.end.imag]
                    self.specs['path'].append(('L', numbers))
                        

                elif isinstance(segment, svgpathtools.CubicBezier):
                    numbers = [segment.control1.real, segment.control1.imag, segment.control2.real, segment.control2.imag, segment.end.real, segment.end.imag]
                    
                    self.specs['path'].append(('C',numbers))
                    
                
                else:
                    raise Exception(f'Path type not supported: {segment}')
                last_end = segment.end
        except ValueError as e:
            if "nan" in path_str:
                regex = r"[A-Za-z](-?nan\s?){2}"
                path_str = re.sub(regex, '', path_str)
                self.path_from_str(path_str)
            else:
                print(f"An error occured while parsine string {path_str}\nIgnoring..")
                raise e
                pass

   
    # Common to each subclass
    def force_style(self, style=None):
        if style == (None, None, None, None):
            return

        color = style[0] 
        opacity = style[1]
        stroke = style[2] 
        stroke_width = style[3] 

        if self.specs['color'] == '#000000' and color is not None and color != 'none':
            self.specs['color'] = color

        if self.specs['opacity'] == 1 and opacity is not None:
            self.specs['opacity'] = opacity

        if self.specs['stroke'] is  None and stroke is not None:
            if stroke == 'currentColor':
                stroke = color
            self.specs['stroke'] = stroke

        if self.specs['stroke-width'] == 1 and stroke_width is not None:
            self.specs['stroke-width'] = stroke_width



    def _apply_matrix(self,params):
        tmp_path =[]
        for c, points in self.specs['path']:
            new_points = []
            if c in 'MCL':
                for x,y in zip(points[::2],points[1::2]):
                    x_new = x*params[0]+y*params[2]+params[4]
                    new_points.append(x_new)
                    y_new = x*params[1]+y*params[3]+params[5]
                    new_points.append(y_new)
            elif c == 'A':
                x_new = points[0]*params[0]+points[1]*params[2]+params[4]
                new_points.append(x_new)
                y_new = points[0]*params[1]+points[1]*params[3]+params[5]
                new_points.append(y_new)
                new_points.append(points[2])
                new_points.append(points[3])
                new_points.append(points[4])
                x_new = points[5]*params[0]+points[6]*params[2]+params[4]
                new_points.append(x_new)
                y_new = points[5]*params[1]+points[6]*params[3]+params[5]
                new_points.append(y_new)

            tmp_path.append((c,new_points))
        self.specs['path']=tmp_path


    def apply_transform(self,trans_list):
        if self.specs['path'] != []:
            for trans in trans_list[::-1]:
                trans = parse_transform(trans)
                if len(trans) > 1:
                    trans.reverse()
                for tr, param in trans:
                    if tr == 'matrix':
                        assert len(param) == 6
                        self._apply_matrix(param)

                    if tr == 'translate':
                        assert len(param) > 0 and len(param) < 3
                        if len(param) == 2:
                            self._apply_matrix([1,0,0,1,param[0],param[1]])
                        else:
                            self._apply_matrix([1,0,0,1,param[0],param[0]])

                    if tr == 'scale':
                        assert len(param) > 0 and len(param) < 3 # if len == 1, sx=sy=param
                        if len(param) == 1:
                            param.append(param[0])
                        self._apply_matrix([param[0],0,0,param[1],0,0])
                        
                    
                    if tr == 'rotate':
                        if len(param) == 1:
                            self._apply_matrix([math.cos(math.radians(param[0])),math.sin(math.radians(param[0])),-math.sin(math.radians(param[0])),math.cos(math.radians(param[0])),0,0])
                        elif len(param) == 3:
                            self._apply_matrix([1,0,0,1,-param[1],-param[2]])
                            self._apply_matrix([math.cos(math.radians(param[0])),math.sin(math.radians(param[0])),-math.sin(math.radians(param[0])),math.cos(math.radians(param[0])),0,0])
                            self._apply_matrix([1,0,0,1,param[1],param[2]])
                        else:
                            raise Exception(f"Cannot manage such transformation {tr} {param}")
    
    def extract_from_ET(self,path):
        path_parsed = path.get('d')
        self.path_from_str(path_parsed)
        self.set_color_from_et(path)
        if path.get('transform') is not None:
            self.apply_transform([path.get('transform')])



class Rectangle(PathSVG):
    def __init__(self,style, original_size):
        super().__init__(style)
        self.original_size = original_size

    def extract_from_ET(self, rect_et):

        x = rect_et.get('x', '0')
        if '%' in x:
            perc = x.split('%')[0]
            x = (float(perc)/100)*self.original_image_size[0]
        x = float(x) 
        
        y = rect_et.get('y', '0')
        if '%' in y:
            perc = y.split('%')[0]
            y = (float(perc)/100)*self.original_image_size[1]
        y = float(y) 

        
        width = rect_et.get('width')
        if width.endswith('%'):
            perc = width.split('%')[0]
            width = (float(perc)/100)*self.original_image_size[0]
        else:
            width = width.strip('px')
        width = float(width)

        height = rect_et.get('height')
        if '%' in height:
            perc = height.split('%')[0]
            height = (float(perc)/100)*self.original_image_size[1]
        height = float(height)
        rx = float(rect_et.get('rx', '0'))  
        ry = float(rect_et.get('ry', '0'))
        
        
        self.path_from_str(convert_rect_to_path(x, y, width, height,rx ,ry))
        self.set_color_from_et(rect_et)


class Circle(PathSVG):

    def __init__(self,style):
        super().__init__(style)

    def extract_from_ET(self, circle):
        cx = float(circle.get('cx', '0')) 
        cy = float(circle.get('cy', '0'))  
        r = float(circle.get('r'))

        self.path_from_str(convert_circle_to_path(cx, cy, r))
        self.set_color_from_et(circle)


class Ellipse(PathSVG):

    def __init__(self,style):
        super().__init__(style)

    def extract_from_ET(self, ellipse):
        cx = float(ellipse.get('cx', '0')) 
        cy = float(ellipse.get('cy', '0'))  
        rx = float(ellipse.get('rx'))
        ry = float(ellipse.get('ry'))

        self.path_from_str(convert_ellipse_to_path(cx, cy, rx, ry))
        self.set_color_from_et(ellipse)


class Polygon(PathSVG):
    def __init__(self,style):
        super().__init__(style)

    def extract_from_ET(self, poly):
        points = poly.get('points')
        self.path_from_str(convert_poly_to_path(points, polygon=True))
        self.set_color_from_et(poly)


        
class Line(PathSVG):
    def __init__(self,style):
        super().__init__(style)

    def extract_from_ET(self, line):
        x1 = line.get('x1', '0')
        y1 = line.get('y1', '0')
        x2 = line.get('x2', '0')
        y2 = line.get('y2', '0')
        self.path_from_str(convert_line_to_path(x1,y1,x2,y2))
        self.set_color_from_et(line)


class Polyline(PathSVG):
    def __init__(self,style):
        super().__init__(style)

    def extract_from_ET(self, polyline):
        points = polyline.get('points')
        self.path_from_str(convert_poly_to_path(points, polygon=False))
        self.set_color_from_et(polyline)


class SVG:
    def __init__(self, viewBox, size=(512,512), maintain_aspect_ratio=False):
        self.svg = list()
        self.path_debug = PathSVG()
        viewBox = list(viewBox)
        if len(viewBox) == 2:
            viewBox.insert(0,0)
            viewBox.insert(0,0)
        self.viewBox = viewBox      
        self.size = size
        self.maintain_aspect_ratio = maintain_aspect_ratio

    def add(self, obj):
        
        self.svg.append(obj)


    def resize_path_points(self, approx = 0):

        if self.maintain_aspect_ratio:
            max_v = (max(self.viewBox[2], self.viewBox[3]),max(self.viewBox[2], self.viewBox[3]))
            offset = [(self.size[0] - (self.size[0]*self.viewBox[2]) / max_v[0] ) / 2 , (self.size[1] - (self.size[1]*self.viewBox[3]) / max_v[1] ) / 2]
        else:
            offset = [0,0]
            max_v = (self.viewBox[2], self.viewBox[3])


        for svg_el in self.svg:
            for p,(c,points) in enumerate(svg_el.specs['path']):
                    new_points = []
                    if len(points) > 0:
                        if c in 'MCL':
                            for px, py in zip(points[::2], points[1::2]):
                                valx = (px/max_v[0])*self.size[0] + offset[0]
                                valy = (py/max_v[1])*self.size[1] + offset[1]
                                new_points.append(round(valx,approx))
                                new_points.append(round(valy,approx)) 
                            svg_el.specs['path'][p] = (c, new_points)
                        elif c == 'A':
                            try:
                                new_points = []
                                new_points.append(round((points[0]*self.size[0]/max_v[0]),approx))
                                new_points.append(round((points[1]*self.size[1]/max_v[1]),approx))
                                new_points.append(points[2])
                                new_points.append(points[3])
                                new_points.append(points[4])
                                new_points.append(round((points[5]*self.size[0]/max_v[0]) + offset[0],approx))
                                new_points.append(round((points[6]*self.size[1]/max_v[1]) + offset[1],approx))
                                svg_el.specs['path'][p] = (c, new_points)
                            except IndexError:
                                raise Exception(f"IndexError: {points}")
                                pass
                        else:
                            raise Exception(f"Unrecognized command! Command: {c} points: {points}")
                        



    # formatted svg, useful for checking svg integrity
    def __str__(self):
        try:
            self.resize_path_points(approx=0)
        except Exception as e:
            print(f"self.viewBox {self.viewBox}")
            raise e
            
        self.out = ""
        
        self.out = f"""<?xml version="1.0" encoding="utf-8"?> 
<!-- Automatically adapted to use only paths with M, A, C and L command, fixed size 512x512 --> 
<svg viewBox="0  0 {self.size[0]}  {self.size[1]}" version="1.1" xmlns="http://www.w3.org/2000/svg">\n"""
        
        for svg_el in self.svg:
            try:
                tmp_path = f"<path style=\""
                
                if svg_el.specs['opacity'] != 1:
                    tmp_path += f"opacity:{svg_el.specs['opacity']};"
                
                if svg_el.specs['color'] != '#000000':
                    tmp_path += f"fill:{svg_el.specs['color']};"

                if svg_el.specs['stroke'] is not None and svg_el.specs['stroke'] != 'none':
                    
                    tmp_path += f"stroke:{svg_el.specs['stroke']};"

                if '' != str(svg_el.specs['stroke-width']):
                    if 'px' in str(svg_el.specs['stroke-width']):
                        stroke_width = float(svg_el.specs['stroke-width'].strip('px')) * ((self.size[0]+self.size[1])/2)/((self.viewBox[2]+self.viewBox[3])/2)
                    elif '%' in str(svg_el.specs['stroke-width']):
                        stroke_width = float(svg_el.specs['stroke-width'].strip('%')) * ((self.size[0]+self.size[1])/2)/((self.viewBox[2]+self.viewBox[3])/2)
                    elif 'pt' in str(svg_el.specs['stroke-width']):
                        stroke_width = float(svg_el.specs['stroke-width'].strip('pt')) * ((self.size[0]+self.size[1])/2)/((self.viewBox[2]+self.viewBox[3])/2)

                    else:
                        stroke_width = float(svg_el.specs['stroke-width']) * ((self.size[0]+self.size[1])/2)/((self.viewBox[2]+self.viewBox[3])/2)
                    def_stroke_width = round(stroke_width+0.51)
                    if def_stroke_width != 1:

                        tmp_path += f"stroke-width:{def_stroke_width};"
                

                tmp_path += "\"\td=\""

                for c,points in svg_el.specs['path']:
                    tmp_path += f"{c}"
                    if len(points) > 0:
                        for px in points[:-1]:
                            tmp_path+=f"{int(px)},"
                        tmp_path += f"{int(points[-1])} "
                tmp_path += "\" />\n"
                self.out += tmp_path
            
            except Exception as e:
                print(e, e.__traceback__.tb_lineno)
                pass
        self.out += "</svg>"
        return self.out
    
    

                