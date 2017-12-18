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
        # If only one polygon is returned in the list, then it should be exactly this polygon.
        edge_list = []
        queue = [[edge, 0] for edge in self.EdgeList()]
        queue += [[edge, 1] for edge in cutting_polygon.EdgeList()]
        epsilon = 1e-7
        while len(queue) > 0:
            new_edge = queue.pop()
            for i in range(len(edge_list)):
                old_edge = edge_list[i]
                lerp_valueA, lerp_valueB = new_edge[0].IntersectWith(old_edge[0])
                if lerp_valueA is not None and lerp_valueB is not None:
                    if epsilon < lerp_valueA < 1.0 - epsilon and -epsilon <= lerp_valueB <= 1.0 + epsilon:
                        point = new_edge[0].Lerp(lerp_valueA)
                        queue.append([LineSegment(new_edge[0].pointA, point), new_edge[1]])
                        queue.append([LineSegment(point, new_edge[0].pointB), new_edge[1]])
                        if epsilon < lerp_valueB < 1.0 - epsilon:
                            del edge_list[i]
                            point = old_edge[0].Lerp(lerp_valueB)
                            edge_list.append([LineSegment(old_edge[0].pointA, point), old_edge[1]])
                            edge_list.append([LineSegment(point, old_edge[0].pointB), old_edge[1]])
                        break
                if new_edge[0].IsSegment(old_edge[0]):
                    break
                if old_edge[0].IsParallelWith(new_edge[0]):
                    break_again = False
                    for point in [new_edge[0].pointA, new_edge[0].pointB]:
                        if old_edge[0].ContainsPoint(point) and not old_edge[0].EitherPointIs(point):
                            del edge_list[i]
                            edge_list.append([LineSegment(old_edge[0].pointA, point), old_edge[1]])
                            edge_list.append([LineSegment(point, old_edge[0].pointB), old_edge[1]])
                            break_again = True
                            break
                    if break_again:
                        break
                    break_again = False
                    for point in [old_edge[0].pointA, old_edge[0].pointB]:
                        if new_edge[0].ContainsPoint(point) and not new_edge[0].EitherPointIs(point):
                            queue.append([LineSegment(new_edge[0].pointA, point), new_edge[1]])
                            queue.append([LineSegment(point, new_edge[0].pointB), new_edge[1]])
                            break_again = True
                            break
                    if break_again:
                        break
            else:
                edge_list.append(new_edge)
        polygon_list = []
        while True:
            polygon = Polygon()
            for i in range(len(edge_list)):
                edge = edge_list[i]
                if edge[1] == 0:
                    edge[1] = 2
                    polygon.point_list.append(edge[0].pointA)
                    leading_edge = edge[0]
                    j = i
                    break
            else:
                break
            while True:
                candidates = []
                for i in range(len(edge_list)):
                    if i != j:
                        edge = edge_list[i]
                        if edge[0].pointA.IsPoint(leading_edge.pointB):
                            candidates.append((edge[0], i))
                        elif edge[0].pointB.IsPoint(leading_edge.pointB):
                            candidates.append((edge[0].Negated(), i))
                if len(candidates) == 0:
                    break
                largest_angle = -math.pi
                best_edge = None
                for edge in candidates:
                    angle = leading_edge.Direction().SignedAngle(edge[0].Direction())
                    if angle > largest_angle:
                        largest_angle = angle
                        best_edge = edge
                if polygon.point_list[0].IsPoint(best_edge[0].pointA):
                    break
                polygon.point_list.append(best_edge[0].pointA)
                leading_edge = best_edge[0]
                edge = edge_list[best_edge[1]]
                if edge[1] == 0:
                    edge[1] = 2
                j = best_edge[1]
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