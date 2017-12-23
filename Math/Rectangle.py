# Rectangle.py

import copy

from Math.LineSegment import LineSegment

class Rectangle(object):
    def __init__(self, min_point, max_point):
        self.min_point = min_point
        self.max_point = max_point

    def Clone(self):
        return copy.deepcopy(self)

    def CalcUVs(self, point):
        u = (point.x - self.min_point.x) / (self.max_point.x - self.min_point.x)
        v = (point.y - self.min_point.y) / (self.max_point.y - self.min_point.y)
        return u, v

    def Width(self):
        return self.max_point.x - self.min_point.x

    def Height(self):
        return self.max_point.y - self.min_point.y

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
            delta_height = (self.Height() - rectangle.Width() * self.Width() / rectangle.Width()) / 2.0
            self.min_point.y += delta_height
            self.max_point.y -= delta_height

    def Center(self):
        return LineSegment(self.min_point, self.max_point).Lerp(0.5)