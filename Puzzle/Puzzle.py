# Puzzle.py

import os
import random

from PIL import Image
from Math.Polygon import Polygon
from Puzzle.Render import Renderer

class Puzzle(object):
    def __init__(self):
        self.cutter_list = []
        self.shape_list = []
        self.base_image_file = None

    def IsSolved(self):
        pass # The puzzle is solved if all shapes have the identity transform.

    def Manipulate(self):
        # TODO: Here we cut, capture and transform...
        pass

    def GenerateImageFile(self, target_image_file):
        # I wanted to use OpenGL to do my off-screen rendering.  Unfortunately,
        # however, (and I think this is super lame), there is no way to create
        # a platform-independent, off-screen OpenGL context.  There may be a
        # good reason for that, but it's still super-duper lame.  So here I'm
        # just rasterizing everything myself.

        with Image.open(self.base_image_file) as base_image:
            base_image_data = base_image.convert('RGB')

            target_image = Image.new('RGB', base_image.width, base_image.height)
            target_image_data = target_image.load()

            renderer = Renderer(base_image, base_image_data, target_image, target_image_data)
            renderer.SetPlaneWindow(-10.0, 10.0, -10.0, 10.0)

            triangle_vertex_stream = [
                (-10.0, -10.0, 0.0, 0.0),
                (10.0, -10.0, 1.0, 0.0),
                (-10.0, 10.0, 0.0, 1.0),
                (10.0, -10.0, 1.0, 0.0),
                (10.0, 10.0, 1.0, 1.0),
                (-10.0, 10.0, 0.0, 1.0)
            ]

            for shape in self.shape_list:
                triangle_vertex_stream += shape.GenerateTriangleVertexStream(renderer)

            renderer.RasterizeTriangles(triangle_vertex_stream)

            target_image.save(target_image_file)

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

    def GenerateTriangleVertexStream(self, renderer):
        triangle_vertex_stream = []
        world_polygon = self.GenerateWorldPolygon()
        world_polygon.Tessellate()
        world_to_local_transform = self.local_to_world_transform.Inverted()
        for triangle in world_polygon.triangle_list:
            for i in range(3):
                world_point = triangle.vertex_list[i]
                local_point = world_to_local_transform.Transform(world_point)
                u = renderer.x_interval.LerpValue(local_point.x)
                v = renderer.y_interval.LerpValue(local_point.y)
                triangle_vertex_stream.append((world_point.x, world_point.y, u, v))
        return triangle_vertex_stream

class Cutter(object):
    def __init__(self):
        self.polygon = None

def RandomImage(image_dir):
    image_list = []
    for directory, dir_list, file_list in os.walk(image_dir):
        for file in file_list:
            if file.endswith('.png'):
                image_list.append(directory + '/' + file)
    i = random.randint(0, len(image_list)-1)
    return image_list[i]

if __name__ == '__main__':
    puzzle = Puzzle()
    puzzle.base_image_file = RandomImage(r'C:\SymmetryGroupPuzzle\Images')
    puzzle.GenerateImageFile(r'C:\SymmetryGroupPuzzle\Images\result.png')