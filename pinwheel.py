# -*- coding: utf-8 -*-
"""
Created on Tue Jan 31 09:24:17 2023

@author: Alex Yeh
"""

import math
from random import randint
from collections import namedtuple

class Point(namedtuple('Point', 'x y')):
    def __repr__(self):
        return f'Point({float(self.x):0.2f}, {float(self.y):0.2f})'
    
    def __add__(self, b):
        return Point(self.x + b.x, self.y + b.y)
    
    def __sub__(self, b):
        return Point(self.x - b.x, self.y - b.y)
    
    def __mul__(self, b):
        return Point(self.x*b, self.y*b)
    
    def __rmul__(self, b):
        return Point(self.x*b, self.y*b)
    
    def __truediv__(self, b):
        return Point(self.x/b, self.y/b)
    
    def __eq__(self, b):
        return self.x == b.x and self.y == b.y
    
    def __hash__(self):
        return hash((self.x, self.y))
    
    def __ne__(self, b):
        return self.x != b.x or self.y != b.y
    
    def magnitude(self):
        """Returns distance to origin"""
        return math.sqrt(self.x**2 + self.y**2)

def intersection(l1, l2, l3, l4):
    """Returns the intersection of two lines"""
    px_numer = (l1.x*l2.y - l1.y*l2.x)*(l3.x - l4.x) - (l1.x - l2.x)*(l3.x*l4.y - l3.y*l4.x)
    py_numer = (l1.x*l2.y - l1.y*l2.x)*(l3.y - l4.y) - (l1.y - l2.y)*(l3.x*l4.y - l3.y*l4.x)
    denom = (l1.x - l2.x)*(l3.y - l4.y) - (l1.y - l2.y)*(l3.x - l4.x)
    
    assert denom != 0, "lines cannot be parallel or coincident"
    
    return Point(px_numer/denom, py_numer/denom)

def divided(p1, p2, factor):
    """Returns a Point spaced factor of the way from p1 to p2"""
    diff = Point(p2.x-p1.x, p2.y-p1.y)
    return Point(p1.x + diff.x*factor, p1.y + diff.y*factor)

def move_along(p1, p2, dist):
    """Returns the point dist along the line from p1 to p2"""
    diff = Point(p2.x-p1.x, p2.y-p1.y)
    unit = diff/diff.magnitude()
    return p1 + unit*dist

def move_direction(p, vec, dist=1):
    """moves p along vec for dist"""
    unit = vec/vec.magnitude()
    return p + unit*dist

def midpoint(p1, p2):
    """Returns a Point midway between p1 and p2"""
    x = (p1.x + p2.x)/2
    y = (p1.y + p2.y)/2
    return Point(x, y)

def limit(val, low=0, high=256):
    """returns 0 if val<0 and 256 if val >256"""
    if val < low:
        return 0
    if val > high:
        return high
    return val

def rgb_step(rgb_tuple, size=8):
    """Given an rgb tuple, steps up size in each color, capped between 0 and 256"""
    dr = randint(-size, size)
    dg = randint(-size, size)
    db = randint(-size, size)
    
    rgb_tuple = (limit(rgb_tuple[0]+dr), 
                 limit(rgb_tuple[1]+dg), 
                 limit(rgb_tuple[2]+db))
    
    return rgb_tuple

def rgb_advance(rgb_tuple, rgb_dir, size=4, memory=0.5):
    """Advances rgb tuple one step along given direction, with specified random noise"""
    drgb_tuple = (randint(-size, size), randint(-size, size), randint(-size, size))
    rgb_tuple = tuple([curr+vec+noise for curr, vec, noise in zip(rgb_tuple, rgb_dir, drgb_tuple)])
    rgb_dir = tuple([int(vec+noise/memory) for vec, noise in zip(rgb_dir, drgb_tuple)])
    return rgb_tuple, rgb_dir

def rgb_to_hex(rgb_tuple):
    """Given a tuple of ints from 0-256, returns a string corresponding to a hex color code"""
    code = ""
    for channel in rgb_tuple:
        if channel < 16:  #requires padding
            code += '0' + hex(channel)[2:]
        else:
            code += hex(channel)[2:]
    return code

class Triangle:
    def __init__(self, a, b, c, strokewidth=1, sizelimit=2.5, 
                 color=(128, 128, 128), color_vec=(0,0,0)):
        """Each vertex of the 1,2,sqrt(5) triangle is saved as diagrammed below.
         a
         |\
         | \
         |  \
        c----b
        """
        self.a = a
        self.b = b 
        self.c = c
        self.com = (a+b+c)/3 # center of mass
        self.size = (b-c).magnitude() # length of shortest side
        
        self.strokewidth = strokewidth
        self.sizelimit = sizelimit
        self.color = color
        self.color_vec = color_vec
        
        rise = (self.b.y - self.a.y)
        run = (self.b.x - self.a.x)
        if run != 0:
            self.slope = rise/run
        else:
            self.slope = float('infinity')
    
    def __repr__(self):
        return f"tip:{self.a}, side:{self.b}, square:{self.c}"
    
    def __eq__(self, tri):
        return self.a == tri.a and self.b == tri.b and self.c == tri.c
    
    def __hash__(self):
        return hash((self.a, self.b, self.c))
    
    def __ne__(self, b):
        return self.a != tri.a or self.b != tri.b or self.c != tri.c
    
    def offset(self, p):
        """adds p to each point in triangle"""
        return Triangle(self.a + p, self.b + p, self.c + p,
                        strokewidth = self.strokewidth,
                        sizelimit = self.sizelimit,
                        color = self.color, color_vec = self.color_vec)
    
    def inset(self, inset=None):
        """Returns the intersections of ab, bc, ca inset by the specified about"""
        if inset is None:
            inset = self.strokewidth/2
            
        ii = divided(self.b, self.a, 1/5)
        ab_dir = self.c - ii
        bc_dir = self.a - self.c
        ca_dir = self.b - self.c
        
        #move each point along two directions perpendicular to adjoining edges
        ab_inset_a = move_direction(self.a, ab_dir, inset)
        ab_inset_b = move_direction(self.b, ab_dir, inset)
        bc_inset_b = move_direction(self.b, bc_dir, inset)
        bc_inset_c = move_direction(self.c, bc_dir, inset)
        ca_inset_c = move_direction(self.c, ca_dir, inset)
        ca_inset_a = move_direction(self.a, ca_dir, inset)
        
        #find intersection of adjoining pairs of inset lines
        a_inset = intersection(ab_inset_a, ab_inset_b, ca_inset_c, ca_inset_a)
        b_inset = intersection(ab_inset_a, ab_inset_b, bc_inset_c, bc_inset_b)
        c_inset = intersection(ca_inset_c, ca_inset_a, bc_inset_c, bc_inset_b)
        
        return a_inset, b_inset, c_inset
        
    def subdivide(self):
        """Subdivides the current triangle and returns tuple of 5 smaller triangles
        """
        i = divided(self.a, self.b, 2/5)
        ii = divided(self.b, self.a, 1/5)
        iii = midpoint(self.c, ii, )
        iv = midpoint(self.a, self.c)
        
        #get 5 random colors
        #colors = [rgb_step(self.color) for i in range(5)]
        colors = [rgb_advance(self.color, self.color_vec) for i in range(5)]
        
        return (Triangle(self.a, iv, i, color = colors[0][0], color_vec = colors[0][1],
                         strokewidth=self.strokewidth, sizelimit=self.sizelimit),
                Triangle(ii, iv, i, color = colors[1][0], color_vec = colors[1][1],
                         strokewidth=self.strokewidth, sizelimit=self.sizelimit),
                Triangle(iv, ii, iii, color = colors[2][0], color_vec = colors[2][1],
                         strokewidth=self.strokewidth, sizelimit=self.sizelimit),
                Triangle(self.c, self.b, ii, color = colors[3][0], color_vec = colors[3][1],
                         strokewidth=self.strokewidth, sizelimit=self.sizelimit),
                Triangle(iv, self.c, iii, color = colors[4][0], color_vec = colors[4][1],
                         strokewidth=self.strokewidth, sizelimit=self.sizelimit))
    
    def svg(self, style=None):
        """Returns string containing svg path following the triangle.
        """
        if style is None:
            style = f'style="fill:none;stroke:#ffffff;stroke-width:{self.strokewidth};stroke-linejoin:round"'
        return f'<path {style} d="M{self.a.x} {self.a.y} L{self.b.x} {self.b.y} L{self.c.x} {self.c.y} Z"/>\n'

    def svg_center_tabs(self, tab_size = 0.2):
        style = 'style="fill:none;stroke:#ff0000;stroke-width:0.1;stroke-linejoin:round"'
        
        a_inset, b_inset, c_inset = self.inset()
        
        ab_mid = midpoint(a_inset, b_inset)
        bc_mid = midpoint(b_inset, c_inset)
        ca_mid = midpoint(c_inset, a_inset)
        
        #calculate segments so that there is a tab with tab_size at midpoint
        ab_amid = move_along(ab_mid, a_inset, tab_size/2)
        ab_bmid = move_along(ab_mid, b_inset, tab_size/2)
        bc_bmid = move_along(bc_mid, b_inset, tab_size/2)
        bc_cmid = move_along(bc_mid, c_inset, tab_size/2)
        ca_cmid = move_along(ca_mid, c_inset, tab_size/2)
        ca_amid = move_along(ca_mid, a_inset, tab_size/2)
        
        
        first = f'<path {style} d="M{ca_amid.x} {ca_amid.y} L {a_inset.x} {a_inset.y} L {ab_amid.x} {ab_amid.y}"/>'
        second = f'<path {style} d="M{ab_bmid.x} {ab_bmid.y} L {b_inset.x} {b_inset.y} L {bc_bmid.x} {bc_bmid.y}"/>'
        third = f'<path {style} d="M{bc_cmid.x} {bc_cmid.y} L {c_inset.x} {c_inset.y} L {ca_cmid.x} {ca_cmid.y}"/>\n'
        return first + second + third

    def svg_tabs(self, tab_size = 0.25):
        style = 'style="fill:none;stroke:#ff0000;stroke-width:0.1;stroke-linejoin:round"'
        
        a_inset, b_inset, c_inset = self.inset()
        
        rt5 = math.sqrt(5)
        
        #calculate segments so that there is tab_size between end of each line
        ab = move_along(a_inset, b_inset,       rt5 * tab_size)
        ba = move_along(b_inset, a_inset,   (rt5/2) * tab_size)
        bc = move_along(b_inset, c_inset,       0.5 * tab_size)
        cb = move_along(c_inset, b_inset,   (rt5/5) * tab_size)
        ca = move_along(c_inset, a_inset, (2*rt5/5) * tab_size)
        ac = move_along(a_inset, c_inset,         2 * tab_size)
        
        first = f'<path {style} d="M{ab.x} {ab.y} L {ba.x} {ba.y}"/> '
        second = f'<path {style} d="M{bc.x} {bc.y} L {cb.x} {cb.y}"/> '
        third = f'<path {style} d="M{ca.x} {ca.y} L {ac.x} {ac.y}"/>\n'
        return first + second + third
    
    def svg_curve(self):
        """returns curvy svg"""
        i = divided(self.a, self.b, 2/5)
        ii = divided(self.b, self.a, 1/5)
        iii = midpoint(self.c, ii, )
        iv = midpoint(self.a, self.c)
        style = f'style="fill:none;stroke:#ff0000;stroke-width:{self.strokewidth};stroke-linejoin:round"'
        
        # first =  f'<path {style} d="M{self.a.x} {self.a.y} Q {self.b.x} {self.b.y} {iv.x} {iv.y}'
        # second = f'Q {self.c.x} {self.c.y} {ii.x} {ii.y}'
        # third = f'Q {self.a.x} {self.a.y} {i.x} {i.y}"/>\n'
        first =  f'<path {style} d="M{self.a.x} {self.a.y} Q {self.com.x} {self.com.y} {self.b.x} {self.b.y}'
        second = f'Q {iii.x} {iii.y} {self.c.x} {self.c.y}'
        third = f'Q {iii.x} {iii.y} {self.a.x} {self.a.y}"/>\n'
        return first + second + third
    
    def svg_filled(self):
        """returns svg with triangle filled with it's color and no border"""
        style = f'style="fill:#{rgb_to_hex(self.color)};stroke:#{rgb_to_hex(self.color)};stroke-width:0.1;stroke-linejoin:round"'
        return f'<path {style} d="M{self.a.x} {self.a.y} L{self.b.x} {self.b.y} L{self.c.x} {self.c.y} Z"/>\n'
        
def subdivide_all(coll):
    """Given a set of Triangles, calls subdivide for each Triangle and returns a single list"""
    assert len(coll) > 0, "subdivide requires a non empty list"
    
    temp = set()
    for tri in list(coll):
        current = coll.pop()
        if tri.size > tri.sizelimit:
            temp.update(current.subdivide())
        else:
            temp.add(current)
    return temp

def subdivide_rand(coll, n, cutoff=5):
    """Given a set of Triangles, calls subdivide and then updates set n times.
    
    If the triangle is subdivided so that it is near in size to it's 
    strokewidth, then it will be added onto a separate set that is returned."""
    assert len(coll) > 0, "subdivide requires a non empty list"
    
    min_size = set()
    for _ in range(n):
        if len(coll) ==0:
            return min_size
        current = coll.pop()
        if current.size > current.sizelimit:
            coll.update(current.subdivide())
        else:
            min_size.add(current)
    return min_size
    
def rect(p1, p2, p3, p4, style=None):
    """Returns a rectangular path"""
    if style is None:
        style = f'style="fill:none;stroke:#ff0000;stroke-width:0.1;stroke-linejoin:round"'
    return f'<path {style} d="M{p1.x} {p1.y} L{p2.x} {p2.y} L{p3.x} {p3.y} L{p4.x} {p4.y} Z"/>\n'
    
svg_opening = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<!-- Created with Inkscape (http://www.inkscape.org/) -->

<svg
   width="8.5in"
   height="11in"
   viewBox="0 0 215.9 279.4"
   version="1.1"
   id="svg5"
   xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"
   xmlns:sodipodi="http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd"
   xmlns="http://www.w3.org/2000/svg"
   xmlns:svg="http://www.w3.org/2000/svg">
"""

svg_ending = '\n</svg>'

if __name__=="__main__":
    
    base = 80
    x_off = Point(4.5, 0)
    y_off = Point(0, 4.5)
    a =     Point(0, 2 * base) + x_off + y_off
    b =     Point(base, 0) + x_off + y_off
    c =     x_off + y_off
    d =     a + b - (x_off + y_off)
    
    shapes = set([Triangle(a, b, c, sizelimit=5),
                  *Triangle(b, a, d, sizelimit=5).subdivide()])
    min_shapes = set()
    
    for level in range(9):
        min_shapes.update(subdivide_rand(shapes, 50*level))
        # shapes = subdivide_all(shapes)
    
        filename = f'pinwheel_level{level}.svg'
        with open(filename, 'w', encoding='utf-8') as f:
            print(len(min_shapes) + len(shapes))
            f.write(svg_opening)
            for tri in shapes:
                f.write(tri.svg_center_tabs())
                f.write(tri.svg())
            for tri in min_shapes:
                f.write(tri.svg_center_tabs())
                f.write(tri.svg())
            f.write(rect(Point(0,0), 
                         (a - x_off) + y_off, 
                         d + x_off + y_off,
                         (b - y_off) + x_off))
            f.write(rect(Point(0,0), 
                         Point(8*25.4, 0),
                         Point(8*25.4, 10.5*25.4),
                         Point(        0, 10.5*25.4)))
            
            bc_len = 5
            first_vertex = a + 2*y_off
            shift = Point(2 * bc_len, 0)
            for tab_size in (0.1, 0.15, 0.2, 0.25, 0.5):
                small = Triangle(first_vertex, 
                                 first_vertex + Point(0, 2*bc_len),
                                 first_vertex + Point(bc_len, 0))
                f.write(small.svg_center_tabs(tab_size = tab_size))
                first_vertex += shift
            f.write(svg_ending)
            
    # with open(filename, 'w', encoding='utf-8') as f:
    #     pass
    
    