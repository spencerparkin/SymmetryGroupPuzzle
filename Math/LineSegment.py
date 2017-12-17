# LineSegment.py

class LineSegment(object):
    def __init__(self, pointA, pointB):
        self.pointA = pointA
        self.pointB = pointB

    def Lerp(self, lerp_value):
        return self.pointA + lerp_value * (self.pointB - self.pointA)

    def Length(self):
        return self.Direction().Length()

    def Direction(self):
        return self.pointB - self.pointA

    def IntersectWith(self, line_segment):
        numerA = (line_segment.pointB - line_segment.pointA).Cross(self.pointA - line_segment.pointA)
        numerB = (line_segment.pointA - line_segment.pointB).Cross(self.pointB - line_segment.pointB)
        denom = (self.pointB - self.pointA).Cross(line_segment.pointB - line_segment.pointA)
        try:
            lerp_valueA = numerA / denom
            lerp_valueB = numerB / denom
        except ZeroDivisionError:
            return None
        return lerp_valueA, lerp_valueB