# LineSegment.py

class LineSegment(object):
    def __init__(self, pointA, pointB):
        self.pointA = pointA
        self.pointB = pointB

    def Lerp(self, lerp_value):
        return self.pointA + lerp_value * (self.pointB - self.pointA)

    def IntersectWith(self, line_segment):
        numer = (line_segment.pointB - line_segment.pointA).Cross(self.pointA - line_segment.pointA)
        denom = (self.pointB - self.pointA).Cross(line_segment.pointB - line_segment.pointA)
        try:
            lerp_value = numer / denom
        except ZeroDivisionError:
            return None
        return lerp_value