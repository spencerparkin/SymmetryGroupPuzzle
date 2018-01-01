# Vector.py

import math

class Vector(object):
    # These are just vectors in the plane.
    def __init__(self, x=0.0, y=0.0):
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

    def __neg__(self):
        return self.Negated()

    def Dot(self, vector):
        return self.x * vector.x + self.y * vector.y

    def Cross(self, vector):
        return self.x * vector.y - self.y * vector.x
    
    def Length(self):
        return math.sqrt(self.Dot(self))
    
    def Polar(self, radius, angle):
        self.x = radius * math.cos(angle)
        self.y = radius * math.sin(angle)
        return self
    
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
        return Vector(self.x * cos_angle - self.y * sin_angle, self.x * sin_angle + self.y * cos_angle)
    
    def Reflected(self, normal):
        parallel, orthogonal = self.Decompose(normal)
        return parallel - orthogonal
    
    def Decompose(self, normal):
        parallel = normal.Scaled(self.Dot(normal))
        orthogonal = self - parallel
        return parallel, orthogonal

    def IsPoint(self, point, epsilon=1e-7):
        return True if (self - point).Length() < epsilon else False

    def Angle(self, vector):
        return math.acos(self.Normalized().Dot(vector.Normalized()))

    def SignedAngle(self, vector):
        angle = self.Angle(vector)
        cross = self.Cross(vector)
        if cross < 0.0:
            angle = -angle
        return angle

    def Lerp(self, vectorA, vectorB, lerp_value):
        lerp_vector = vectorA + lerp_value * (vectorB - vectorA)
        self.x = lerp_vector.x
        self.y = lerp_vector.y
        return self

    def ProjectOnto(self, normal):
        return (self.Dot(normal) / normal.Dot(normal)) * normal

    def RejectFrom(self, normal):
        return self - self.ProjectOnto(normal)