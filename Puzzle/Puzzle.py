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
    def __init__(self, cutter_list, window):
        self.cutter_list = cutter_list
        self.window = window
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
                if inside_list is not None and len(inside_list) > 0:
                    for outside_polygon in outside_list:
                        queue.append(outside_polygon)
                    break
            else:
                self.shape_list.append(Shape(polygon))
    
    def PerformAction(self, action):
        cutter = self.cutter_list[action.cutter_offset]
        symmetry_transform = cutter.symmetry_list[action.symmetry_offset]
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
            action = Action().Random(self)
            self.PerformAction(action)
            count -= 1

    def RenderShadow(self):
        for cutter in self.cutter_list:
            cutter.RenderShadow()

    def RenderShapes(self):
        for shape in self.shape_list:
            shape.Render(self.window)

    '''def NearestCutter(self, point):
        j = -1
        shortest_distance = 0.0
        for i, cutter in enumerate(self.cutter_list):
            distance = (point - cutter.polygon.AveragePoint()).Length()
            if j < 0 or distance < shortest_distance:
                j = i
                shortest_distance = distance
        return j'''

    def DeterminePossibleActions(self, mouse_point):
        # TODO: Render a ccw, cw and reflection action indicated by the given point.
        #       The applicable cutter is closest to the given point.  The rotation actions
        #       are the smallest available of the cutter.  The reflection of the cutter
        #       is found as having an axis (eigen vector) closest to that vector formed by
        #       the average point of the cutter polygon and the mouse point.
        return None, None, None

class Shape(object):
    def __init__(self, polygon, transform=None):
        self.polygon = polygon
        # There is some concern that this will suffer from accumulated round-off error.
        self.transform = transform if transform is not None else AffineTransform()
        # The render transform will lag behind the actual transform for animation purposes.
        self.render_transform = AffineTransform()
    
    def Transformed(self):
        return self.polygon.Transformed(self.transform)
    
    def Render(self, window):
        self.polygon.TesselateIfNeeded()
        glBegin(GL_TRIANGLES)
        try:
            for triangle in self.polygon.triangle_list:
                for i in range(3):
                    point = triangle.vertex_list[i]
                    u, v = window.CalcUVs(point)
                    glTexCoord2f(u, v)
                    #point = self.render_transform * point  TODO: When ready to animate, re-enable this.
                    point = self.transform * point # TODO: Do this for now.  Everything will instantly snap into place.  Delete later.
                    glVertex2f(point.x, point.y)
        finally:
            glEnd() # Failing to call this is apparently fatal.
    
class Cutter(object):
    def __init__(self, polygon=None):
        self.polygon = polygon if polygon is not None else Polygon()
        # Each transform in this list, when applied to the polygon, produces a symmetry of the polygon.
        # One way to think of each symmetry transform is as a permutation of the vertices of the polygon.
        # Of course, not all permutations of the vertices would be valid.
        self.symmetry_list = []

    def RenderShadow(self):
        glColor3f(0.0, 0.0, 0.0)
        self.polygon.TesselateIfNeeded()
        self.polygon.RenderTriangles()

    def RenderOutline(self):
        glColor3f(1.0, 1.0, 1.0)
        glLineWidth(2.0)
        self.polygon.RenderEdges()

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

class Action(object):
    def __init__(self):
        self.cutter_offset = None
        self.symmetry_offset = None

    def Random(self, puzzle):
        self.cutter_offset = random.randint(0, len(puzzle.cutter_list) - 1)
        cutter = puzzle.cutter_list[self.cutter_offset]
        self.symmetry = random.randint(0, len(cutter.symmetry_list) - 1)
        return self

    def Render(self, puzzle):
        cutter = puzzle.cutter_list[self.cutter_offset]
        cutter.RenderOutline()
        # TODO: If we're a reflection, draw the reflection axis.