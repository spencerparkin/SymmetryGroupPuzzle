# Triangle.py

import math

from Math.Vector import Vector

class Triangle(object):
    # These are planar triangles.  If the points are ordered
    # counter-clockwise, they have positive area; if ordered
    # clockwise, negative area.
    def __init__(self, vertexA=None, vertexB=None, vertexC=None):
        self.vertex_list = [vertexA, vertexB, vertexC]

    def Serialize(self):
        data = {
            'vertex_list': [vertex.Serialize() for vertex in self.vertex_list]
        }
        return data

    def Deserialize(self, data):
        self.vertex_list = [Vector().Deserialize(vertex) for vertex in data['vertex_list']]
        return self

    def SignedArea(self):
        return (self.vertex_list[1] - self.vertex_list[0]).Cross(self.vertex_list[2] - self.vertex_list[0]) / 2.0

    def IsDegenerate(self, epsilon=1e-7):
        return math.fabs(self.SignedArea()) < epsilon

    def ContainsPoint(self, point, epsilon=1e-7):
        for i in range(3):
            j = (i + 1) % 3
            area = Triangle(self.vertex_list[i], self.vertex_list[j], point).SignedArea()
            if area <= -epsilon:
                return False
        return True