# Triangle.py

class Triangle(object):
    # These are planar triangles.  If the points are ordered
    # counter-clockwise, they have positive area; if ordered
    # clockwise, negative area.
    def __init__(self, vertexA, vertexB, vertexC):
        self.vertexA = vertexA
        self.vertexB = vertexB
        self.vertexC = vertexC

    def SignedArea(self):
        return (self.vertexB - self.vertexA).Cross(self.vertexC - self.vertexA) / 2.0

    def ContainsPoint(self, point, epsilon=1e-7):
        pass