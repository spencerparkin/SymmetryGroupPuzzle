# Vector.py

import math

def Vector(object):
    # These are just vectors in the plane.
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y)

    def __mul__(self, other):
        return self.Scaled(other)
    
    def __rmul__(self, other):
        return self.Scaled(other)

    def Dot(self, other):
        return self.x * other.x + self.y * other.y

    def Cross(self, other):
        return self.x * other.y - self.y * other.x
    
    def Length(self):
        return math.sqrt(self.Dot(self))
    
    def Polar(self, radius, angle):
        self.x = radius * math.cos(angle)
        self.y = radius * math.sin(angle)
    
    def Negated(self):
        return Vector(-self.x, -self.y)
    
    def Scaled(self, scale):
        return Vector(self.x * scale, self.y * scale)
    
    def Normalized(self):
        try:
            return self.Scaled(1.0 / self.Length())
        except ZeroDivisionError:
            return None
    
    def Rotated(self, angle):
        sin_angle = math.sin(angle)
        cos_angle = math.cos(angle)
        return Vector(self.x * sin_angle + self.y * cos_angle, -self.x * sin_angle + self.y * cos_angle)
    
    def Reflected(self, normal):
        parallel, orthogonal = self.Decompose(normal)
        return parallel - orthogonal
    
    def Decompose(self, normal):
        parallel = normal.Scaled(self.Dot(normal))
        orthogonal = self - parallel
        return parallel, orthogonal