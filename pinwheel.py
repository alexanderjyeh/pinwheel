# -*- coding: utf-8 -*-
"""
Created on Tue Jan 31 09:24:17 2023

@author: Alex Yeh
"""

import math
from random import sample
from collections import namedtuple

import matplotlib.pyplot as plt
import numpy as np

class Point(namedtuple('Point', 'x y')):
    def __repr__(self):
        return f'Point({float(self.x):0.2f}, {float(self.y):0.2f})'
    
    def __add__(self, b):
        return Point(self.x + b.x, self.y + b.y)
    
    def __sub__(self, b):
        return Point(self.x - b.x, self.y - b.y)
    
    def __mul__(self, b):
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

def shrink_line(p1, p2, dist):
    """Returns first and last point on the line segment which is 2*dist shorter
    than p1-p2"""
    p1p2 = move_along(p1, p2, dist)
    p2p1 = move_along(p2, p1, dist)
    return p1p2, p2p1

def midpoint(p1, p2):
    """Returns a Point midway between p1 and p2"""
    x = (p1.x + p2.x)/2
    y = (p1.y + p2.y)/2
    return Point(x, y)

class Triangle:
    def __init__(self, a, b, c, strokewidth=1, sizelimit=2.5):
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
        rise = (self.b.y - self.a.y)
        run = (self.b.x - self.a.x)
        if run != 0:
            self.slope = rise/run
        else:
            self.slope = np.Inf
    
    def __repr__(self):
        return f"tip:{self.a}, side:{self.b}, square:{self.c}"
    
    def __eq__(self, tri):
        return self.a == tri.a and self.b == tri.b and self.c == tri.c
    
    def __hash__(self):
        return hash((self.a, self.b, self.c))
    
    def __ne__(self, b):
        return self.a != tri.a or self.b != tri.b or self.c != tri.c
    
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
        
        return (Triangle(self.a, iv, i, strokewidth=self.strokewidth, sizelimit=self.sizelimit),
                Triangle(ii, iv, i, strokewidth=self.strokewidth, sizelimit=self.sizelimit),
                Triangle(iv, ii, iii, strokewidth=self.strokewidth, sizelimit=self.sizelimit),
                Triangle(self.c, self.b, ii, strokewidth=self.strokewidth, sizelimit=self.sizelimit),
                Triangle(iv, self.c, iii, strokewidth=self.strokewidth, sizelimit=self.sizelimit))
    
    def svg(self, style=None):
        """Returns string containing svg path following the triangle.
        """
        if style is None:
            style = f'style="fill:none;stroke:#ff0000;stroke-width:{self.strokewidth};stroke-linejoin:round"'
        return f'<path {style} d="M{self.a.x} {self.a.y} L{self.b.x} {self.b.y} L{self.c.x} {self.c.y} Z"/>\n'

    def svg_tabs(self, tab_size=0.1):
        style = 'style="fill:none;stroke:#ff0000;stroke-width:0.1;stroke-linejoin:round"'
        
        a_inset, b_inset, c_inset = self.inset()
        
        #calculate segments with small tab at inset
        ab = move_along(a_inset, b_inset, 4*tab_size)
        ba = move_along(b_inset, a_inset, 2*tab_size)
        bc = move_along(b_inset, c_inset, tab_size) 
        cb = move_along(c_inset, b_inset, 1.5*tab_size)
        ca = move_along(c_inset, a_inset, 1.5*tab_size)
        ac = move_along(a_inset, c_inset, 4*tab_size)
        
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
        
def subdivide_all(coll):
    """Given a collection of objects, calls subdivide for each object and returns a single list"""
    assert len(coll) > 0, "subdivide requires a non empty list"
    
    temp = []
    for shape in coll:
        temp.extend(shape.subdivide())
    return temp

def subdivide_rand(coll, n, cutoff=5):
    """Given a set of Triangles, calls subdivide and then updates set n times.
    
    If the triangle is subdivided so that it is near in size to it's 
    strokewidth, then it will be added onto a separate set that is returned."""
    assert len(coll) > 0, "subdivide requires a non empty list"
    
    min_size = set()
    for i in range(n):
        if len(coll) ==0:
            return min_size
        current = coll.pop()
        if current.size > current.sizelimit:
            coll.update(current.subdivide())
        else:
            min_size.add(current)
    return min_size
    
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
    
    offset = Point(10, 10)
    a = Point(0,254) + offset
    b = Point(127,0) + offset
    c = offset
    d = a+b-offset
    
    shapes = set([Triangle(a, b, c, sizelimit=5),
                  *Triangle(b, a, d, sizelimit=5).subdivide()])
    min_shapes = set()
    for level in range(10):
        min_shapes.update(subdivide_rand(shapes, 200*level))
    
        filename = f'pinwheel_level{level}.svg'
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(svg_opening)
            for tri in shapes:
                f.write(tri.svg_tabs())
            for tri in min_shapes:
                f.write(tri.svg_tabs())
            f.write(svg_ending)
    
    #%%
    shapes.update(min_shapes)
    sizes, slopes = [], []
    for tri in shapes:
        sizes.append(tri.size)
        slopes.append(tri.slope)
    
    sizes = np.array(sizes)
    slopes = np.array(slopes)
    
    fig, axs = plt.subplots(1, 2,
                            gridspec_kw=dict(left=0.05, right=0.99,
                                             bottom=0.1, top=0.9))
    axs[0].hist(sizes, bins=np.linspace(sizes.min(), sizes.max()))
    axs[0].set_title("size distribution")
    axs[1].hist(slopes[np.isfinite(slopes)], bins=np.linspace(-6,6))
    axs[1].set_title("hypotenuse slope distribution")
    
    