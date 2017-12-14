# Polygon.py

import copy

from Triangle import Triangle
from LineSegment import LineSegment

class Polygon(object):
    # These may be convex or concave polygons in the plane.
    # The list of vertices is always ordered counter-clockwise.
    def __init__(self):
        self.point_list = []
        self.triangle_list = []

    def Clone(self):
        return copy.deepcopy(self)

    def Reduce(self):
        pass # Here, remove all redundant vertices.  The second of three consecutive collinear points, for example.

    def EdgeList(self):
        edge_list = []
        for i in range(len(self.point_list)):
            j = (i + 1) % len(self.point_list)
            edge = LineSegment(self.point_list[i], self.point_list[j])
            edge_list.append(edge)
        return edge_list

    def Cut(self, cutting_polygon):
        # Here we cut this polygon against the given polygon into one or more returned polygons.
        edge_list = []
        queue = [(edge, True) for edge in self.EdgeList()]
        queue += [(edge, False) for edge in cutting_polygon.EdgeList()]
        epsilon = 1e-7
        while len(queue) > 0:
            new_edge = queue.pop()
            for i in range(len(edge_list)):
                old_edge = edge_list[i]
                lerp_valueA, lerp_valueB = new_edge[0].IntersectWith(old_edge[0])
                if epsilon < lerp_valueA < 1.0 - epsilon and -epsilon <= lerp_valueB <= 1.0 + epsilon:
                    point = new_edge[0].Lerp(lerp_valueA)
                    queue.append((LineSegment(new_edge[0].pointA, point), new_edge[1]))
                    queue.append((LineSegment(point, new_edge[0].pointB), new_edge[1]))
                    if epsilon < lerp_valueB < 1.0 - epsilon:
                        del edge_list[i]
                        point = old_edge[0].Lerp(lerp_valueB)
                        edge_list.append((LineSegment(old_edge[0].pointA, point), old_edge[1]))
                        edge_list.append((LineSegment(point, old_edge[0].pointB), old_edge[1]))
                    break
            else:
                edge_list.append(new_edge)
        while True:
            for i in range(len(edge_list)):
                edge = edge_list[i]
                if edge[1]:
                    break
            else:
                break
            # TODO: Follow cycle, building up a polygon to add to the returned list.
            #       Once constructed, remove non-cutting edges used in construction from edge list.

    def Tessellate(self):
        # Here we find a triangle list that is a tessellation of this polygon.
        # This is not only useful for rendering, but also for determining whether a given
        # point lies somewhere inside the polygon.
        if len(self.point_list) < 3:
            return None
        polygon = self.Clone()
        self.triangle_list = []
        epsilon = 1e-7
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
                            lerp_valueA, lerp_valueB = line_segment.IntersectWith(edge)
                            if epsilon < lerp_valueA < 1.0 - epsilon or \
                                epsilon < lerp_valueB < 1.0 - epsilon:
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