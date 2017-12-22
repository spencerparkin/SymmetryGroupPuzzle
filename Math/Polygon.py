# Polygon.py

import math
import copy

from Math.Triangle import Triangle
from Math.LineSegment import LineSegment

class Polygon(object):
    # These may be convex or concave polygons in the plane.
    # The list of vertices is always ordered counter-clockwise.
    def __init__(self, point_list = None):
        self.point_list = point_list if point_list is not None else []
        self.triangle_list = []

    def Clone(self):
        return copy.deepcopy(self)

    def Tessellate(self, epsilon=1e-7):
        if len(self.point_list) < 3:
            return None
        polygon = self.Clone()
        self.triangle_list = []
        while True:
            if len(polygon.point_list) == 3:
                self.triangle_list.append(Triangle(polygon.point_list[0], polygon.point_list[1], polygon.point_list[2]))
                break
            else:
                for i in range(len(polygon.point_list)):
                    j = (i + 1) % len(polygon.point_list)
                    k = (i + 2) % len(polygon.point_list)
                    triangle = Triangle(polygon.point_list[i], polygon.point_list[j], polygon.point_list[k])
                    area = triangle.SignedArea()
                    if area > 0:
                        line_segment = LineSegment(polygon.point_list[i], polygon.point_list[k])
                        for edge in self.GenerateEdges():
                            point = line_segment.IntersectionPoint(edge)
                            if point is not None and not line_segment.EitherPointIs(point):
                                break
                        else:
                            self.triangle_list.append(triangle)
                            del polygon.point_list[j]
                            break
    
    def ContainsPoint(self, point):
        for triangle in self.triangle_list:
            if triangle.ContainsPoint(point):
                return True
        return False
    
    def CutAgainst(self, polygon):
        # Split this polygon against the given polygon into one or more polygons.
        # Return two lists of polygons: those found inside the given polygon, and
        # then those found outside of it.  Note that we do not support the ability
        # for the cutting polygon to punch a "hole" in this polygon.
        if len(polygon.triangle_list) == 0:
            polygon.Tessellate()
        #...
    
    def GenerateEdges(self):
        for i in range(len(self.point_list)):
            j = (i + 1) % len(self.point_list)
            yield LineSegment(self.point_list[i], self.point_list[j])
    
    def Transformed(self, transform):
        polygon = Polygon()
        for point in self.point_list:
            polygon.poing_list.append(transform.Transform(point))
        return polygon

''' Actualy, I think what follows is crap...delete it later...
class Graph(object):
    def __init__(self):
        self.edge_list = []
    
    def AddEdge(self, edge, label, replace_existing=True):
        queue = [(edge, label)]
        while len(queue) > 0:
            edge = queue.pop()
            for i, existing_edge in enumerate(self.edge_list):
                if edge[0].IsSegment(existing_edge[0]):
                    if replace_existing:
                        self.edge_list[i] = edge
                    break
            else:
                for i, existing_edge in enumerate(self.edge_list):
                    found = False
                    for point in [existing_edge[0].pointA, existing_edge[0].pointB]:
                        if not edge[0].EitherPointIs(point) and edge[0].ContainsPoint(point):
                            queue.append((LineSegment(edge[0].pointA, point), edge[1]))
                            queue.append((LineSegment(point, edge[0].pointB), edge[1]))
                            found = True
                            break
                    else:
                        for point in [edge[0].pointA, edge[0].pointB]:
                            if not existing_edge[0].EitherPointIs(point) and existing_edge[0].ContainsPoint(point):
                                del self.edge_list[i]
                                self.edge_list.append((LineSegment(existing_edge[0].pointA, point), existing_edge[1]))
                                self.edge_list.append((LineSegment(point, existing_edge[0].pointB), existing_edge[1]))
                                found = True
                                break
                    if found:
                        break
                else:
                    for i, existing_edge in enumerate(self.edge_list):
                        point = edge[0].IntersectionPoint(existing_edge[0])
                        if point is not None:
                            queue.append((LineSegment(edge[0].pointA, point), edge[1]))
                            queue.append((LineSegment(point, edge[0].pointB), edge[1]))
                            del self.edge_list[i]
                            self.edge_list.append((LineSegment(existing_edge[0].pointA, point), existing_edge[1]))
                            self.edge_list.append((LineSegment(point, existing_edge[0].pointB), existing_edge[1]))
                            break
    
    def FindEdgeWithLabel(self, label, remove=True):
        for i, edge in enumerate(self.edge_list):
            if edge[1] == label:
                if remove:
                    del self.edge_list[i]
                return edge
    
    def GenerateEdgesWithPoint(self, point):
        for edge in self.edge_list:
            if edge[0].pointA.IsPoint(point):
                yield edge
            elif edge[0].pointB.IsPoint(point):
                edge[0].Negate()
                yield edge
'''