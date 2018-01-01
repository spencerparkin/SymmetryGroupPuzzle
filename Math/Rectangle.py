# Rectangle.py

import copy

from Math.Vector import Vector
from Math.LineSegment import LineSegment
from Math.Polygon import Polygon

class Rectangle(object):
    def __init__(self, min_point=None, max_point=None):
        self.min_point = min_point if min_point is not None else Vector(0.0, 0.0)
        self.max_point = max_point if max_point is not None else Vector(0.0, 0.0)

    def Clone(self):
        return copy.deepcopy(self)

    def CalcUVs(self, point):
        u = (point.x - self.min_point.x) / (self.max_point.x - self.min_point.x)
        v = (point.y - self.min_point.y) / (self.max_point.y - self.min_point.y)
        return u, v

    def ApplyUVs(self, u, v):
        x = self.min_point.x + u * (self.max_point.x - self.min_point.x)
        y = self.min_point.y + v * (self.max_point.y - self.min_point.y)
        return Vector(x, y)

    def Map(self, point, rectangle):
        u, v = self.CalcUVs(point)
        return rectangle.ApplyUVs(u, v)

    def Width(self):
        return self.max_point.x - self.min_point.x

    def Height(self):
        return self.max_point.y - self.min_point.y

    def Area(self):
        return self.Width() * self.Height()

    def AspectRatio(self):
        return self.Width() / self.Height()

    def ExpandToMatchAspectRatioOf(self, rectangle):
        aspect_ratioA = self.AspectRatio()
        aspect_ratioB = rectangle.AspectRatio()
        if aspect_ratioA > aspect_ratioB:
            delta_height = (rectangle.Height() * self.Width() / rectangle.Width() - self.Height()) / 2.0
            self.min_point.y -= delta_height
            self.max_point.y += delta_height
        else:
            delta_width = (rectangle.Width() * self.Height() / rectangle.Height() - self.Width()) / 2.0
            self.min_point.x -= delta_width
            self.min_point.y += delta_width

    def ContractToMatchAspectRatioOf(self, rectangle):
        aspect_ratioA = self.AspectRatio()
        aspect_ratioB = rectangle.AspectRatio()
        if aspect_ratioA > aspect_ratioB:
            delta_width = (self.Width() - rectangle.Width() * self.Height() / rectangle.Height()) / 2.0
            self.min_point.x += delta_width
            self.max_point.x -= delta_width
        else:
            delta_height = (self.Height() - rectangle.Height() * self.Width() / rectangle.Width()) / 2.0
            self.min_point.y += delta_height
            self.max_point.y -= delta_height

    def Center(self):
        return LineSegment(self.min_point, self.max_point).Lerp(0.5)

    def GrowForPoint(self, point):
        # Minimally grow the rectangle to include the given point.
        if self.min_point.x > point.x:
            self.min_point.x = point.x
        if self.max_point.x < point.x:
            self.max_point.x = point.x
        if self.min_point.y > point.y:
            self.min_point.y = point.y
        if self.max_point.y < point.y:
            self.max_point.y = point.y

    def Scale(self, scale_factor):
        center = self.Center()
        max_vector = self.max_point - center
        min_vector = self.min_point - center
        max_vector = max_vector.Scaled(scale_factor)
        min_vector = min_vector.Scaled(scale_factor)
        self.max_point = center + max_vector
        self.min_point = center + min_vector

    def Polygon(self):
        polygon = Polygon()
        polygon.point_list.append(Vector(self.min_vector.x, self.min_vector.y))
        polygon.point_list.append(Vector(self.max_vector.x, self.min_vector.y))
        polygon.point_list.append(Vector(self.max_vector.x, self.max_vector.y))
        polygon.point_list.append(Vector(self.min_vector.x, self.max_vector.y))
        return polygon