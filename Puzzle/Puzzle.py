# Puzzle.py

from Math.Polygon import Polygon

class Puzzle(object):
    def __init__(self):
        self.cutter_list = []
        self.shape_list = []

    def IsSolved(self):
        pass # The puzzle is solved if all shapes have the identity transform.

    def Manipulate(self):
        # TODO: Here we cut, capture and transform...
        pass

    def GenerateTriangleVertexStream(self, x_interval, y_interval):
        x_min = x_interval.min_point
        x_max = x_interval.max_point
        y_min = y_interval.min_point
        y_max = y_interval.max_point
        
        triangle_vertex_stream = [
            (x_min, y_min, 0.0, 0.0),
            (x_max, y_min, 1.0, 0.0),
            (x_min, y_max, 0.0, 1.0),
            (x_max, y_min, 1.0, 0.0),
            (x_max, y_max, 1.0, 1.0),
            (x_min, y_max, 0.0, 1.0)
        ]

        for shape in self.shape_list:
            triangle_vertex_stream += shape.GenerateTriangleVertexStream(x_interval, y_interval)
        
        return triangle_vertex_stream

class Shape(object):
    def __init__(self):
        self.local_polygon = None
        # This might suffer from accumulated round-off error.  Hmmm...
        # To combat that, would keeping a history of transforms help, even if it slowed things down?
        self.local_to_world_transform = None

    def GenerateWorldPolygon(self):
        world_polygon = Polygon()
        for point in self.local_polygon.point_list:
            point = self.local_to_world_transform.Transform(point)
            world_polygon.point_list.append(point)
        return world_polygon

    def GenerateTriangleVertexStream(self, x_interval, y_interval):
        triangle_vertex_stream = []
        world_polygon = self.GenerateWorldPolygon()
        world_polygon.Tessellate()
        world_to_local_transform = self.local_to_world_transform.Inverted()
        for triangle in world_polygon.triangle_list:
            for i in range(3):
                world_point = triangle.vertex_list[i]
                local_point = world_to_local_transform.Transform(world_point)
                u = x_interval.LerpValue(local_point.x)
                v = y_interval.LerpValue(local_point.y)
                triangle_vertex_stream.append((world_point.x, world_point.y, u, v))
        return triangle_vertex_stream

class Cutter(object):
    def __init__(self):
        self.polygon = None