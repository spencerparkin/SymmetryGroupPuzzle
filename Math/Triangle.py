# Triangle.py

class Triangle(object):
    # These are planar triangles.  If the points are ordered
    # counter-clockwise, they have positive area; if ordered
    # clockwise, negative area.
    def __init__(self, vertexA, vertexB, vertexC):
        self.vertex_list = [vertexA, vertexB, vertexC]

    def SignedArea(self):
        return (self.vertex_list[1] - self.vertex_list[0]).Cross(self.vertex_list[2] - self.vertex_list[0]) / 2.0

    def ContainsPoint(self, point):
        for i in range(3):
            j = (i + 1) % 3
            area = Triangle(self.vertex[i], self.vertex[j], point).SignedArea()
            if area < 0.0:
                return False
        return True