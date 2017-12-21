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
                        for u in range(len(polygon.point_list)):
                            v = (u + 1) % len(polygon.point_list)
                            edge = LineSegment(polygon.point_list[u], polygon.point_list[v])
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
        pass
    
    def Transformed(self, transform):
        polygon = Polygon()
        for point in self.point_list:
            polygon.poing_list.append(transform.Transform(point))
        return polygon