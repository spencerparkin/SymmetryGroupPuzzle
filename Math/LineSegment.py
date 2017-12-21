# LineSegment.py

import math

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

    def Negated(self):
        return LineSegment(self.pointB, self.pointA)

    def IsParallelWith(self, line_segment, epsilon=1e-7):
        if math.fabs(self.Direction().Cross(line_segment.Direction())) < epsilon:
            return True
        return False

    def IsSegment(self, line_segment, epsilon=1e-7):
        if self.pointA.IsPoint(line_segment.pointA, epsilon) and self.pointB.IsPoint(line_segment.pointB, epsilon):
            return True
        if self.pointA.IsPoint(line_segment.pointB, epsilon) and self.pointB.IsPoint(line_segment.pointA, epsilon):
            return True
        return False

    def IntersectWith(self, line_segment):
        numerA = (line_segment.pointB - line_segment.pointA).Cross(self.pointA - line_segment.pointA)
        numerB = (self.pointB - self.pointA).Cross(line_segment.pointA - self.pointA)
        denom = (self.pointB - self.pointA).Cross(line_segment.pointB - line_segment.pointA)
        try:
            lerp_valueA = numerA / denom
            lerp_valueB = numerB / -denom
        except ZeroDivisionError:
            return None, None
        return lerp_valueA, lerp_valueB

    def IntersectionPoint(self, line_segment, epsilon=1e-7):
        lerp_valueA, lerp_valueB = self.IntersectWith(line_segment)
        if lerp_valueA is not None and lerp_valueB is not None:
            if -epsilon <= lerp_valueA <= 1.0 + epsilon and -epsilon <= lerp_valueB <= 1.0 + epsilon:
                return self.Lerp(lerp_valueA)

    def LerpValueOf(self, point, epsilon=1e-7):
        vectorA = self.pointB - self.pointA
        vectorB = point - self.pointA
        cross = vectorA.Cross(vectorB)
        if math.fabs(cross) >= epsilon:
            return None
        lerp_value = vectorA.Dot(vectorB) / vectorA.Dot(vectorA)
        return lerp_value

    def ContainsPoint(self, point, epsilon=1e-7):
        lerp_value = self.LerpValueOf(point, epsilon)
        if lerp_value is None:
            return False
        if -epsilon < lerp_value < 1.0 + epsilon:
            return True
        return False

    def EitherPointIs(self, point, epsilon=1e-7):
        return self.pointA.IsPoint(point, epsilon) or self.pointB.IsPoint(point, epsilon)