# Transform.py

from Math.Vector import Vector

class LinearTransform(object):
    def __init__(self, xAxis=Vector(1.0, 0.0), yAxis=Vector(0.0, 1.0)):
        self.xAxis = xAxis
        self.yAxis = yAxis

    def Determinant(self):
        return self.xAxis.Cross(self.yAxis)

    def Inverted(self):
        try:
            inverse = LinearTransform()
            inverse.xAxis = Vector(self.yAxis.y, -self.xAxis.y)
            inverse.yAxis = Vector(-self.xAxis.x, self.yAxis.x)
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

class AffineTransform(object):
    def __init__(self, xAxis=Vector(1.0, 0.0), yAxis=Vector(0.0, 1.0), translation=Vector(0.0, 0.0)):
        self.linear_transform = LinearTransform(xAxis, yAxis)
        self.translation = translation

    def Inverted(self):
        inverse = AffineTransform()
        inverse.linear_transform = self.linear_transform.Inverted()
        if inverse.linear_transform is None:
            return None
        inverse.translation = inverse.linear_transform.Transform(self.translation.Negated())
        return inverse

    def Transform(self, vector):
        return self.linear_transform * vector + self.translation

    def Rotation(self, point, angle):
        pass

    def Reflection(self, point, normal):
        pass

    def RigidMotion(self, angle, translation):
        self.linear_transform.Rotation(angle)
        self.translation = translation

    def __mul__(self, thing):
        if isinstance(thing, AffineTransform):
            affine_transform = AffineTransform()
            affine_transform.linear_transform = self.linear_transform * thing.linear_transform
            affine_transform.translation = self.linear_transform * thing.translation + self.translation
            return affine_transform
        elif isinstance(thing, Vector):
            return self.Transform(thing)