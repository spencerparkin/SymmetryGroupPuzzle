# Puzzle.py

import math
import random

from OpenGL.GL import *
from Math.Vector import Vector
from Math.Polygon import Polygon
from Math.Transform import AffineTransform
from Math.Rectangle import Rectangle

class Puzzle(object):
    # In order to support non-trivial topologies (i.e., shapes with "holes" in them),
    # we'll have to use polygons that are self-tangent.
    def __init__(self, cutter_list):
        self.cutter_list = cutter_list
        # We use the cutting polygons to generate the initial list of shapes.
        # As the game progresses, this list of shapes may be further cut up.
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
        # Calculate a window to encompass all cutter polygons.
        self.window = Rectangle()
        for cutter in self.cutter_list:
            for i in range(len(cutter.polygon.point_list)):
                point = cutter.polygon.point_list[i]
                self.window.GrowForPoint(point)
        self.window.Scale(1.5)

    def Serialize(self):
        # I thought about making JSONEncoder derivative, but this is just easier, I think.
        for shape in self.shape_list:
            shape.polygon.TesselateIfNeeded()
        data = {
            'window': self.window.Serialize(),
            'shape_list': [shape.Serialize() for shape in self.shape_list],
            'cutter_list': [cutter.Serialize() for cutter in self.cutter_list]
        }
        return data

    def Deserialize(self, data):
        # I thought about using an object hook with the JSON decoder, but this is just easier, I think.
        self.window = Rectangle().Deserialize(data['window'])
        self.shape_list = [Shape().Deserialize(shape) for shape in data['shape_list']]
        self.cutter_list = [Cutter().Deserialize(cutter) for cutter in data['cutter_list']]
        return self

    def IsSolved(self):
        pass # We are solved if every shape has the identity transform.

    def RotateCutter(self, i, ccw=True):
        cutter = self.cutter_list[i]
        symmetry_transform = AffineTransform()
        if ccw:
            symmetry_transform.Rotation(cutter.center, cutter.angle_of_symmetry)
        else:
            symmetry_transform.Rotation(cutter.center, -cutter.angle_of_symmetry)
        self._ApplySymmetryTransform(cutter, symmetry_transform)

    def ReflectCutter(self, i, j):
        cutter = self.cutter_list[i]
        axis = cutter.axes_of_symmetry[j]
        symmetry_transform = AffineTransform().Reflection(cutter.center, axis)
        self._ApplySymmetryTransform(cutter, symmetry_transform)

    def _ApplySymmetryTransform(self, cutter, symmetry_transform):
        # Here, the given transform must be a symmetry of the given cutter polygon.
        if not cutter.IsValidSymmetry(symmetry_transform):
            raise Exception('Invalid symmetry!')
        new_shape_list = []
        for shape in self.shape_list:
            inside_list, outside_list = shape.Transformed().CutAgainst(cutter.polygon)
            if len(inside_list) == 0:
                new_shape_list.append(shape)
            elif len(inside_list) == 1 and len(outside_list) == 0:
                # Mathematically, there is no need to handle this case, but by so doing,
                # we avoid a great deal of accumulated round-off error problems.  We don't
                # avoid them altogether, though; we just stave them off until further on.
                shape.transform = symmetry_transform * shape.transform
                new_shape_list.append(shape)
            else:
                inverse_transform = shape.transform.Inverted()
                new_transform = symmetry_transform * shape.transform
                for polygon in outside_list:
                    new_shape_list.append(Shape(polygon.Transformed(inverse_transform), shape.transform))
                for polygon in inside_list:
                    new_shape_list.append(Shape(polygon.Transformed(inverse_transform), new_transform))
        self.shape_list = new_shape_list
    
    def Scramble(self, count):
        while count > 0:
            i = random.randint(0, len(self.cutter_list) - 1)
            if random.randint(0, 1) == 0:
                self.RotateCutter(i, random.randint(0, 1) == 0)
            else:
                cutter = self.cutter_list[i]
                j = random.randint(0, len(cutter.axes_of_symmetry) - 1)
                self.ReflectCutter(i, j)
            count -= 1

    def RenderShadow(self):
        for cutter in self.cutter_list:
            cutter.RenderShadow()

    def RenderShapes(self):
        for shape in self.shape_list:
            shape.Render(self.window)

    def NearestCutter(self, point):
        # TODO: Require point to be inside cutter?
        j = -1
        shortest_distance = 0.0
        for i, cutter in enumerate(self.cutter_list):
            distance = (point - cutter.center).Length()
            if j < 0 or distance < shortest_distance:
                j = i
                shortest_distance = distance
        return j

    def NearestAxisOfSymmetry(self, point):
        i = self.NearestCutter(point)
        cutter = self.cutter_list[i]
        vector = point - cutter.center
        smallest_angle = 2.0 * math.pi
        i = -1
        for j in range(len(cutter.axes_of_symmetry)):
            axis = cutter.axes_of_symmetry[j]
            for normal in [axis, axis.Negated()]:
                angle = normal.Angle(vector)
                if angle < smallest_angle:
                    smallest_angle = angle
                    i = j
        return i

class Shape(object):
    def __init__(self, polygon, transform=None):
        self.polygon = polygon
        # There is some concern that this will suffer from accumulated round-off error.
        # We try to mitigate the problem here a bit by re-orthonormalizing all the time.
        self.transform = transform if transform is not None else AffineTransform()
        self.transform.Orthonormalize()

    def Serialize(self):
        data = {
            'polygon': self.polygon.Serialize(),
            'transform': self.transform.Serialize(),
        }
        return data

    def Deserialize(self, data):
        self.polygon = Polygon().Deserialize(data['polygon'])
        self.transform = AffineTransform().Deserialize(data['transform'])
        return self

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
                    point = self.transform * point
                    glVertex2f(point.x, point.y)
        finally:
            glEnd()
    
class Cutter(object):
    def __init__(self, polygon=None):
        self.polygon = polygon if polygon is not None else Polygon()
        self.angle_of_symmetry = 0.0
        self.axes_of_symmetry = []
        self.center = Vector()

    def Serialize(self):
        data = {
            'polygon': self.polygon.Serialize(),
            'angle_of_symmetry': self.angle_of_symmetry,
            'axes_of_symmetry': [axis.Serialize() for axis in self.axes_of_symmetry],
            'center': self.center.Serialize()
        }
        return data

    def Deserialize(self, data):
        self.polygon = Polygon().Deserialize(data['polygon'])
        self.angle_of_symmetry = data['angle_of_symmetry']
        self.axes_of_symmetry = [Vector().Deserialize(axis) for axis in data['axes_of_symmetry']]
        self.center = Vector().Deserialize(data['center'])
        return self

    def RenderShadow(self):
        glColor3f(0.0, 0.0, 0.0)
        self.polygon.TesselateIfNeeded()
        self.polygon.RenderTriangles()

    def RenderOutline(self):
        self.polygon.RenderEdges()

    def MakeRegularPolygon(self, sides, center, radius, tilt_angle=0.0):
        self.center = center
        self.angle_of_symmetry = 2.0 * math.pi / float(sides)
        self.polygon = Polygon()
        for i in range(sides):
            angle = float(i) / float(sides) * 2.0 * math.pi
            vector = Vector().Polar(radius, angle + tilt_angle)
            point = center + vector
            self.polygon.point_list.append(point)
            self.axes_of_symmetry.append(vector.Normalized())

    def IsValidSymmetry(self, symmetry_transform):
        # Make sure that the given transform permutes the vertices of our polygon.
        point_list = [point for point in self.polygon.point_list]
        for point in self.polygon.point_list:
            point = symmetry_transform.Transform(point)
            for i in range(len(point_list)):
                if point_list[i].IsPoint(point):
                    del point_list[i]
                    break
            else:
                return False
        # Lastly, make sure that the transformed polygon is valid.
        # It must not self-intersect and it must be wound properly in the plane.
        return self.polygon.Transformed(symmetry_transform).IsValid()