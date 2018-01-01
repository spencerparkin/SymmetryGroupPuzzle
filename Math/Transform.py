# Transform.py

import copy

from Math.Vector import Vector
from Math.LineSegment import LineSegment

class LinearTransform(object):
    def __init__(self, xAxis=None, yAxis=None):
        self.xAxis = xAxis if xAxis is not None else Vector(1.0, 0.0)
        self.yAxis = yAxis if yAxis is not None else Vector(0.0, 1.0)

    def Clone(self):
        return copy.deepcopy(self)
    
    def Identity(self):
        self.xAxis = Vector(1.0, 0.0)
        self.yAxis = Vector(0.0, 1.0)
    
    def Determinant(self):
        return self.xAxis.Cross(self.yAxis)

    def Inverted(self):
        try:
            inverse = LinearTransform()
            inverse.xAxis = Vector(self.yAxis.y, -self.xAxis.y)
            inverse.yAxis = Vector(-self.yAxis.x, self.xAxis.x)
            det = self.Determinant()
            inverse = inverse * (1.0 / det)
            return inverse
        except ZeroDivisionError:
            return None

    def Decompose(self):
        pass

    def Transform(self, vector):
        return self.xAxis.Scaled(vector.x) + self.yAxis.Scaled(vector.y)

    def __mul__(self, thing):
        if type(thing) is float:
            return LinearTransform(self.xAxis.Scaled(thing), self.yAxis.Scaled(thing))
        elif isinstance(thing, LinearTransform):
            return LinearTransform(self.Transform(thing.xAxis), self.Transform(thing.yAxis))
        elif isinstance(thing, Vector):
            return self.Transform(thing)

    def Reflection(self, normal):
        self.xAxis = Vector(1.0, 0.0).Reflected(normal)
        self.yAxis = Vector(0.0, 1.0).Reflected(normal)

    def Rotation(self, angle):
        self.xAxis = Vector(1.0, 0.0).Rotated(angle)
        self.yAxis = Vector(0.0, 1.0).Rotated(angle)

    def Scale(self, xScale, yScale):
        self.xAxis = Vector(1.0, 0.0).Scaled(xScale)
        self.yAxis = Vector(0.0, 1.0).Scaled(yScale)

    def Shear(self, shear):
        self.xAxis = Vector(1.0, 0.0)
        self.yAxis = Vector(shear, 1.0)

    def Interpolate(self, transformA, transformB, interp_value):
        pass

    def Orthonormalize(self):
        self.xAxis = self.xAxis.Normalized()
        self.yAxis = self.yAxis.RejectFrom(self.xAxis)
        self.yAxis = self.yAxis.Normalized()

class AffineTransform(object):
    def __init__(self, xAxis=Vector(1.0, 0.0), yAxis=Vector(0.0, 1.0), translation=Vector(0.0, 0.0)):
        self.linear_transform = LinearTransform(xAxis, yAxis)
        self.translation = translation

    def Clone(self):
        return copy.deepcopy(self)

    def Identity(self):
        self.linearTransform.Identity()
        self.translation = Vector(0.0, 0.0)

    def Inverted(self):
        inverse = AffineTransform()
        inverse.linear_transform = self.linear_transform.Inverted()
        if inverse.linear_transform is None:
            return None
        inverse.translation = inverse.linear_transform.Transform(self.translation.Negated())
        return inverse

    def Orthonormalize(self):
        self.linear_transform.Orthonormalize()

    def Transform(self, vector):
        return self.linear_transform * vector + self.translation

    def Rotation(self, point, angle):
        self.linear_transform.Rotation(angle)
        self.translation = self.linear_transform * -point + point
        return self

    def Reflection(self, point, normal):
        self.linear_transform.Reflection(normal)
        self.translation = self.linear_transform * -point + point
        return self

    def Translation(self, translation):
        self.linear_transform.Identity()
        self.translation = translation
        return self

    def RigidBodyMotion(self, angle, translation):
        self.linear_transform.Rotation(angle)
        self.translation = translation
        return self

    def __mul__(self, thing):
        if isinstance(thing, AffineTransform):
            affine_transform = AffineTransform()
            affine_transform.linear_transform = self.linear_transform * thing.linear_transform
            affine_transform.translation = self.linear_transform * thing.translation + self.translation
            return affine_transform
        elif isinstance(thing, Vector):
            return self.Transform(thing)

    def Interpolate(self, transformA, transformB, interp_value):
        self.linear_transform.Interpolate(transformA.linear_transform, transformB.linear_transform, interp_value)
        self.translation.Lerp(transformA.translation, transformB.translation, interp_value)