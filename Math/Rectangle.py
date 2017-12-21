# Rectangle.py

from Math.Vector import Vector

class Rectangle(object):
    def __init__(self, min_point, max_point):
        self.min_point = min_point
        self.max_point = max_point
    
    def CalcUVs(self, point):
        u = (point.x - self.min_point.x) / (self.max_point.x - self.min_point.x)
        v = (point.y - self.min_point.y) / (self.max_point.y - self.min_point.y)
        return u, v