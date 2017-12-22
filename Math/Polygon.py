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
    
    def CutAgainst(self, cutting_polygon):
        # Split this polygon against the given polygon into one or more polygons.
        # Return two lists of polygons: those found inside the given polygon, and
        # then those found outside of it.  Note that we do not support the ability
        # for the cutting polygon to punch a "hole" in this polygon.
        inside_list = []
        outside_list = []
        inside_polygon, outside_polygon = self._SplitAgainst(cutting_polygon)
        if inside_polygon is not None and outside_polygon is not None:
            inside_queue = [inside_polygon]
            outside_queue = [outside_polygon]
            while len(inside_queue) > 0 or len(outside_queue) > 0:
                for queue in [inside_queue, outside_queue]:
                    polygon = queue.pop()
                    inside_polygon, outside_polygon = polygon._SplitAgainst(cutting_polygon)
                    if inside_polygon is not None and outside_polygon is not None:
                        inside_queue.append(inside_polygon)
                        outside_queue.append(outside_polygon)
                    elif queue is inside_queue:
                        inside_list.append(polygon)
                    elif queue is outside_queue:
                        outside_list.append(polygon)
        else:
            # In this case, don't we still need to determine which side we're on?
            return None, None
        return inside_list, outside_list

    def _SplitAgainst(self, cutting_polygon):
        # Split this polygon against the given polygon into two polygons: one found
        # on the inside of the cutting polygon, and the other on the outside.  These
        # two polygons are not necessarily guaranteed to be completely inside or
        # outside the cutting polygon, respectively, but the cut is well defined in
        # that the two polygons are on the proper side of the cutting polygon in a
        # neighborhood of the cut line.  If no cut occurs, then (None, None) is returned.
        pass
    
    def GenerateEdges(self):
        for i in range(len(self.point_list)):
            j = (i + 1) % len(self.point_list)
            yield LineSegment(self.point_list[i], self.point_list[j])
    
    def Transformed(self, transform):
        polygon = Polygon()
        for point in self.point_list:
            polygon.poing_list.append(transform.Transform(point))
        return polygon