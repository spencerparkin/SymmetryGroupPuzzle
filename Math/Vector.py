# Vector.py

import math

def Vector(object):
    # These are just vectors in the plane.
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, vector):
        return Vector(self.x + vector.x, self.y + vector.y)

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar):
        return self.Scaled(scalar)
    
    def __rmul__(self, scalar):
        return self.Scaled(scalar)

    def Dot(self, vector):
        return self.x * vector.x + self.y * vector.y

    def Cross(self, vector):
        return self.x * vector.y - self.y * vector.x
    
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