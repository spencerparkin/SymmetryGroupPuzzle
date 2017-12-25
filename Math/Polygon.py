# Polygon.py

import copy

from OpenGL.GL import *
from Math.Triangle import Triangle
from Math.LineSegment import LineSegment
from Math.Vector import Vector

def CyclicIteration(start, stop, modulus, step=1):
    i = start
    while i != stop:
        yield i
        i = (i + step) % modulus

class Polygon(object):
    # These may be convex or concave polygons in the plane.
    # The list of vertices is always ordered counter-clockwise.
    def __init__(self, point_list = None):
        self.point_list = point_list if point_list is not None else []
        self.triangle_list = []

    def Clone(self):
        return copy.deepcopy(self)

    def AveragePoint(self):
        if len(self.point_list) > 0:
            average_point = Vector(0.0, 0.0)
            for point in self.point_list:
                average_point += point
            average_point = average_point.Scaled(1.0 / float(len(self.point_list)))
            return average_point

    def TesselateIfNeeded(self):
        # Of course, if we already have a tesselation, we have no
        # way of knowing if it is still valid.  Vertices may have
        # been added or removed since it was generated.
        if len(self.triangle_list) == 0:
            self.Tessellate()

    def Tessellate(self, epsilon=1e-7):
        if len(self.point_list) < 3:
            return None
        polygon = self.Clone()
        # The correctness of our algorithm will depend on there being no redundant vertices.
        polygon.RemoveAllRedundantVertices()
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
                            point = line_segment.IntersectionPoint(edge, epsilon)
                            if point is not None and not line_segment.EitherPointIs(point, epsilon):
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

    def ContainsPointOnEdge(self, point, epsilon=1e-7):
        for edge in self.GenerateEdges():
            if edge.ContainsPoint(point, epsilon):
                return True
        return False

    def IsInteriorPoint(self, point, epsilon=1e-7):
        return self.ContainsPoint(point) and not self.ContainsPointOnEdge(point, epsilon)

    def HasVertex(self, point, epsilon=1e-7):
        for vertex in self.point_list:
            if vertex.IsPoint(point, epsilon):
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
                    if len(queue) > 0:
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
        intersection_point_list = []
        for cutting_edge in cutting_polygon.GenerateEdges():
            if self.ContainsPointOnEdge(cutting_edge.pointA):
                intersection_point_list.append(cutting_edge.pointA)
            else:
                hit_list = []
                for edge in self.GenerateEdges():
                    point = edge.IntersectionPoint(cutting_edge)
                    if point is not None and not cutting_edge.EitherPointIs(point):
                        for hit in hit_list:
                            if hit[0].IsPoint(point):
                                break
                        else:
                            lerp_value = cutting_edge.LerpValueOf(point)
                            hit_list.append((point, lerp_value))
                hit_list.sort(key = lambda hit: hit[1])
                intersection_point_list += [hit[0] for hit in hit_list]
        self_clone = self.Clone()
        cutter_clone = cutting_polygon.Clone()
        for point in intersection_point_list:
            self_clone.AddRedundantVertex(point)
            cutter_clone.AddRedundantVertex(point)
        # Now check the adjacent pairs of intersection points.  Note that not all
        # such pairs are valid cuts.  Here we need only find and use one of them.
        # If there is a way to do this without tessellation, it's not immediately
        # obvious to me.
        self.TesselateIfNeeded()
        for i in range(len(intersection_point_list)):
            j = (i + 1) % len(intersection_point_list)
            cut_start = cutter_clone.FindVertex(intersection_point_list[i])
            cut_stop = cutter_clone.FindVertex(intersection_point_list[j])
            valid_cut = False
            for k in CyclicIteration(cut_start, cut_stop, len(cutter_clone.point_list)):
                point = cutter_clone.point_list[k]
                if self.IsInteriorPoint(point):
                    valid_cut = True
                    break
                point = LineSegment(cutter_clone.point_list[k], cutter_clone.point_list[(k + 1) % len(cutter_clone.point_list)]).Lerp(0.5)
                if self.IsInteriorPoint(point):
                    valid_cut = True
                    break
            if valid_cut:
                start = self_clone.FindVertex(intersection_point_list[j])
                stop = self_clone.FindVertex(intersection_point_list[i])
                inside_polygon = Polygon()
                for k in CyclicIteration(cut_start, cut_stop, len(cutter_clone.point_list)):
                    inside_polygon.point_list.append(cutter_clone.point_list[k])
                for k in CyclicIteration(start, stop, len(self_clone.point_list)):
                    inside_polygon.point_list.append(self_clone.point_list[k])
                outside_polygon = Polygon()
                for k in CyclicIteration(cut_stop, cut_start, len(cutter_clone.point_list), -1):
                    outside_polygon.point_list.append(cutter_clone.point_list[k])
                for k in CyclicIteration(stop, start, len(self_clone.point_list)):
                    outside_polygon.point_list.append(self_clone.point_list[k])
                return inside_polygon, outside_polygon
        return None, None

    def AddRedundantVertex(self, point, epsilon=1e-7):
        if self.HasVertex(point, epsilon):
            return False
        for i in range(len(self.point_list)):
            j = (i + 1) % len(self.point_list)
            edge = LineSegment(self.point_list[i], self.point_list[j])
            if edge.ContainsPoint(point, epsilon):
                self.point_list.insert(j, point)
                return True
        raise Exception('Cannot add vertex without altering polygon geometry.')

    def RemoveAllRedundantVertices(self):
        # Remove all cases of 3 or more collinear points.
        while True:
            for i in range(len(self.point_list)):
                j = (i + 1) % len(self.point_list)
                k = (i + 2) % len(self.point_list)
                triangle = Triangle(self.point_list[i], self.point_list[j], self.point_list[k])
                if triangle.IsDegenerate():
                    del self.point_list[j]
                    break
            else:
                break

    def FindVertex(self, point, epsilon=1e-7):
        for i in range(len(self.point_list)):
            if self.point_list[i].IsPoint(point, epsilon):
                return i
        return -1

    def GenerateEdges(self):
        for i in range(len(self.point_list)):
            j = (i + 1) % len(self.point_list)
            yield LineSegment(self.point_list[i], self.point_list[j])
    
    def Transformed(self, transform):
        polygon = Polygon()
        for point in self.point_list:
            polygon.poing_list.append(transform.Transform(point))
        return polygon

    def RenderEdges(self):
        glBegin(GL_LINE_LOOP)
        try:
            for i in range(len(self.point_list)):
                point = self.point_list[i]
                glVertex2f(point.x, point.y)
        finally:
            glEnd()

    def RenderTriangles(self):
        glBegin(GL_TRIANGLES)
        try:
            for triangle in self.triangle_list:
                for i in range(3):
                    point = triangle.vertex_list[i]
                    glVertex2f(point.x, point.y)
        finally:
            glEnd()