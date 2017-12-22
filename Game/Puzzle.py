# Puzzle.py

import math
import random

from OpenGL.GL import *
from Math.Vector import Vector
from Math.Polygon import Polygon
from Math.Transform import AffineTransform

class Puzzle(object):
    # In order to support non-trivial topologies (i.e., shapes with "holes" in them),
    # we'll have to use polygons that self-touch or that are self-tangent.
    def __init__(self, cutter_list):
        self.cutter_list = cutter_list
        self.MakeInitialShapeList()
    
    def IsSolved(self):
        pass # We are solved if every shape has the identity transform.
    
    def MakeInitialShapeList(self):
        # We use the cutting polygons to generate the initial list of shapes.
        # As the game progresses, this list of shapes is further cut up.
        # The shape list is maintained as a set of non-overlapping polygons.
        # The cutter list is a list of polygons where each overlaps one or more others.
        self.shape_list = []
        queue = [cutter.polygon.Clone() for cutter in self.cutter_list]
        while len(queue) > 0:
            polygon = queue.pop()
            for shape in self.shape_list:
                inside_list, outside_list = polygon.CutAgainst(shape.polygon)
                if len(inside_list) > 0:
                    for outside_polygon in outside_list:
                        queue.append(outside_polygon)
                    break
            else:
                self.shape_list.append(Shape(polygon))
    
    def ApplyCuttingPolygon(self, i=-1, j=-1):
        if i < 0:
            i = random.randint(0, len(self.cutter_list) - 1)
        cutter = self.cutter_list[i]
        if j < 0:
            j = random.randint(0, len(cutter.symmetry_list) - 1)
        symmetry_transform = cutter.symmetry_list[j]
        new_shape_list = []
        for shape in self.shape_list:
            inside_list, outside_list = shape.Transformed().CutAgainst(cutter.polygon)
            if len(inside_list) == 0:
                new_shape_list.append(shape)
            else:
                inverse_transform = shape.transform.Inverted()
                new_transform = symmetry_transform * shape.transform
                for polygon in outside_list:
                    new_shape_list.append(Shape(polygon.Transformed(inverse_transform)), shape.transform)
                for polygon in inside_list:
                    new_shape_list.append(Shape(polygon.Transformed(inverse_transform)), new_transform)
        self.shape_list = new_shape_list
    
    def Scramble(self, count):
        while count > 0:
            self.ApplyCuttingShape()
            count -= 1

class Shape(object):
    def __init__(self, polygon, transform=None):
        self.polygon = polygon
        # There is some concern that this will suffer from accumulated round-off error.
        self.transform = transform if transform is not None else AffineTransform()
    
    def Transformed(self):
        return self.polygon.Transformed(self.transform)
    
    def Render(self, rectangle):
        self.polygon.TessellateIfNeeded()
        glBegin(GL_TRIANGLES)
        try:
            for triangle in self.polygon.triangle_list:
                for i in range(3):
                    point = triangle.vertex_list[i]
                    u, v = rectangle.CalcUVs(point)
                    glTexCoord2f(u, v)
                    point = self.transform * point
                    glVertex2f(point.x, point.y)
        finally:
            glEnd() # Failing to call this is apparently fatal.
    
class Cutter(object):
    def __init__(self, polygon=None):
        self.polygon = polygon if polygon is not None else Polygon()
        # Each transform in this list, when applied to the polygon, produces a symmetry of the polygon.
        self.symmetry_list = []

    def MakeRegularPolygon(self, sides, center, radius, tilt_angle=0.0):
        self.polygon = Polygon()
        for i in range(sides):
            angle = float(i) / float(sides) * 2.0 * math.pi
            vector = Vector().Polar(radius, angle + tilt_angle)
            point = center + vector
            self.polygon.point_list.append(point)
            rotation = AffineTransform().Rotation(center, angle)
            reflection = AffineTransform().Reflection(center, vector)
            self.symmetry_list += [rotation, reflection]