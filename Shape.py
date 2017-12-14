# Shape.py

import copy
import math

from Triangle import Triangle
from LineSegment import LineSegment

class Shape(object):
    # These are convex or concave polygons in the plane.
    # The list of vertices is always ordered counter-clockwise.
    # The polygon may overlap itself in any region of the plane
    # as long as that overlap has zero area.  The idea here is
    # that we want to be able to represent polygons with zero
    # or more "holes" in them.  In other words, we want to support
    # a variety of topologies with our shapes, but we want to do
    # this while maintaining a simple and consistent representation;
    # namely, a finite sequence of points in the plane.  Consequently,
    # some points may be repeated in the sequence.
    def __init__(self):
        self.point_list = []
        self.triangle_list = None

    def Clone(self):
        return copy.deepcopy(self)

    def Reduce(self):
        pass # Here, remove all redundant vertices.  The second of three consecutive collinear points, for example.

    def Cut(self, cutting_shape):
        # Here we cut this shape against the given shape into one or more returned shapes.
        pass
        # Start by creating a graph where every edge is directed so that we know which way is clock-wise.
        # In this graph are all the vertices shared between this and the given shape, plus the intersection points.
        # Also, for each edge, we know whether it is one belonging to this shape or the cutting shape.
        # There must exist a path in the graph from any one vertex to another if we want to be able to
        # punch holes in a shape.  Ensuring this, however, by creating additional edges, does not appear to be a trivial task.
        # However, if it can be done correctly or adequitly, then the remainder of our algorithm can proceed without any further considerations.
        # Once we have the graph, the only remaining task is simply to pull all cut shapes from the graph.
        # What this amounts to is visiting all cycles of the graph that do no contain any "chords."  There is one of
        # these for every vertex of the duel plane graph, save the vertex representing the outside area.

    def Tessellate(self):
        # Here we find a triangle list that is a tessellation of this polygon.
        # This is not only useful for rendering, but also for determining whether a given
        # point lies somewhere inside the shape.
        if len(self.point_list) < 3:
            return None
        shape = self.Clone()
        self.triangle_list = []
        while True:
            if len(shape.point_list) == 3:
                self.triangle_list.append(Triangle(shape.point_list[0], shape.point_list[1], shape.point_list[2]))
                break
            else:
                for i in range(len(shape.point_list)):
                    j = (i + 1) % len(shape.point_list)
                    k = (i + 2) % len(shape.point_list)
                    triangle = Triangle(shape.point_list[i], shape.point_list[j], shape.point_list[k])
                    area = triangle.SignedArea()
                    if area > 0:
                        line_segment = LineSegment(shape.point_list[i], shape.point_list[k])
                        if self.FindNonTrivialEdgeIntersectionWith(line_segment) < 0:
                            self.triangle_list.append(triangle)
                            del shape.point_list[j]
                            break

    def FindNonTrivialEdgeIntersectionWith(self, line_segment, epsilon=1e-7):
        for i in range(len(self.point_list)):
            j = (i + 1) % len(self.point_list)
            edge = LineSegment(self.point_list[i], self.point_list[j])
            lerp_valueA = line_segment.IntersectWith(edge)
            lerp_valueB = edge.IntersectWith(line_segment)
            if math.abs(lerp_valueA) >= epsilon and math.abs(1.0 - lerp_valueA) >= epsilon and \
                math.abs(lerp_valueB) >= epsilon and math.abs(1.0 - lerp_valueB) >= epsilon:
                return i
        return -1
    
    def ContainsPoint(self, point):
        for triangle in self.triangle_list:
            if triangle.ContainsPoint(point):
                return True
        return False