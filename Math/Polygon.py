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
        # We don't support the case here were the given polygon would punch a hole in this polygon.
        edge_list = []
        queue = [(edge, 0) for edge in self.EdgeList()]
        queue += [(edge, 1) for edge in cutting_polygon.EdgeList()]
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
        def FindEdge(edge_list, code, preceding_edge=None, remove=False):
            for i in range(len(edge_list)):
                edge = edge_list[i]
                if edge[1] == code:
                    if preceding_edge is None or (edge[0].pointA - preceding_edge.pointB).Length() < epsilon:
                        if remove:
                            del edge_list[i]
                        return edge
        polygon_list = []
        while True:
            new_edge = FindEdge(edge_list, 0, None, True)
            if new_edge is None:
                break
            polygon_edge_list = [new_edge]
            while True:
                old_edge = new_edge
                new_edge = FindEdge(edge_list, 1, old_edge)
                if new_edge is None:
                    new_edge = FindEdge(edge_list, 0, old_edge, True)
                    if new_edge is None:
                        raise Exception('Cutting algorithm failed!')
                if new_edge == polygon_edge_list[0]:
                    break
                polygon_edge_list.append(new_edge)
            polygon = Polygon()
            polygon.point_list = [edge[0].pointA for edge in polygon_edge_list]
            polygon_list.append(polygon)
        return polygon_list

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