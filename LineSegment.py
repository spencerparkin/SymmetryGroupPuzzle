# LineSegment.py

class LineSegment(object):
    def __init__(self, pointA, pointB):
        self.pointA = pointA
        self.pointB = pointB

    def Lerp(self, lerp_value):
        return self.pointA + lerp_value * (self.pointB - self.pointA)

    def IntersectWith(self, line_segment):
        # Here we return the lerp value that, if applied to this segment,
        # would return the intersection point between this segment and
        # the given segment.  If there is no such intersection, then a
        # lerp value outside of [0,1] is returned in the case that the line
        # containing this segment does intersect the given segment, or None otherwise.
        pass # TODO: Return lerp value here.