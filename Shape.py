# Shape.py

import copy

from Vector import Vector
from Triangle import Triangle
from LineSegment import LineSegment

class Shape(object):
    # These are convex or concave polygons in the plane.
    # The list of vertices is ordered counter-clockwise.
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

    def Clone(self):
        return copy.deepcopy(self)

    def Cut(self, cutting_shape):
        # Here we cut this shape by the given shape into one or more returned shapes.
        queue = [self.Clone()]
        shape_list = []
        while len(queue) > 0:
            shape = queue.pop()
            shapeA, shapeB = shape._SplitAgainst(cutting_shape)
            if shapeA and shapeB:
                queue += [shapeA, shapeB]
            elif shapeA:
                queue.append(shapeA)
            else:
                shape_list.append(shape)
        return shape_list

    def _SplitAgainst(self, cutting_shape):
        # Here we try to find any valid split of this shape against the given shape.
        # If none is found, then we may have to punch a hole in the shape and return that.
        # In the remaining case, we return nothing, as the given shape does not split this shape at all.
        pass

    def Tessellate(self):
        # Here we find and return a triangle list that is a tessellation of this polygon.
        # This is not only useful for rendering, but also for determining whether a given
        # point lies somewhere inside the shape.
        if len(self.point_list) < 3:
            return None
        shape = self.Clone()
        triangle_list = []
        while True:
            if len(shape.point_list) == 3:
                triangle_list.append(Triangle(shape.point_list[0], shape.point_list[1], shape.point_list[2]))
                break
            else:
                for i in range(len(shape.point_list)):
                    j = (i + 1) % len(shape.point_list)
                    k = (i + 2) % len(shape.point_list)
                    triangle = Triangle(shape.point_list[i], shape.point_list[j], shape.point_list[k])
                    if triangle.SignedArea() > 0:
                        line_segment = LineSegment(shape.point_list[i], shape.point_list[k])
                        intersection_list = self.FindEdgeIntersectionsWithLineSegment(line_segment)
                        if len(intersection_list) == 0:
                            triangle_list.append(triangle)
                            del shape.point_list[j]
                            break
                else:
                    return None
        return triangle_list

    def FindEdgeIntersectionsWithLineSegment(self, line_segment, epsilon=1e-7):
        # Notice that we treat the given line segment as an open interval here.
        intersection_list = []
        for i in range(len(self.point_list)):
            j = (i + 1) % len(self.point_list)
            edge = LineSegment(self.point_list[i], self.point_list[j])
            lerp_value = line_segment.IntersectWith(edge)
            if lerp_value is not None:
                if 0.0 + epsilon < lerp_value < 1.0 - epsilon:
                    intersection_list.append(lerp_value)
        return intersection_list