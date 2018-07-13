# Puzzle16.py

import math

from Puzzle import Puzzle, CutRegion
from math2d_region import Region, SubRegion
from math2d_vector import Vector
from math2d_polygon import Polygon
from math2d_affine_transform import AffineTransform

class Puzzle16(Puzzle):
    def __init__(self):
        super().__init__()

        sub_region = SubRegion()
        sub_region.polygon.vertex_list.append(Vector(0.0, 0.0))
        sub_region.polygon.vertex_list.append(Vector(0.0, -3.0))
        sub_region.polygon.vertex_list.append(Vector(3.0, -3.0))
        sub_region.polygon.vertex_list.append(Vector(3.0, 0.0))
        cut_region = CutRegion()
        cut_region.region = Region()
        cut_region.region.sub_region_list.append(sub_region)
        self.cut_region_list.append(cut_region)

        cut_region = CutRegion()
        cut_region.region = Region()
        sub_region = SubRegion()
        sub_region.polygon.vertex_list.append(Vector(0.0, 0.0))
        sub_region.polygon.vertex_list.append(Vector(0.0, 1.0))
        sub_region.polygon.vertex_list.append(Vector(-1.0, 1.0))
        sub_region.polygon.vertex_list.append(Vector(-1.0, 0.0))
        cut_region.region.sub_region_list.append(sub_region)
        sub_region = SubRegion()
        sub_region.polygon.vertex_list.append(Vector(2.0, -2.0))
        sub_region.polygon.vertex_list.append(Vector(2.0, -3.0))
        sub_region.polygon.vertex_list.append(Vector(3.0, -3.0))
        sub_region.polygon.vertex_list.append(Vector(3.0, -2.0))
        cut_region.region.sub_region_list.append(sub_region)
        self.cut_region_list.append(cut_region)

        sub_region = SubRegion()
        sub_region.polygon.vertex_list.append(Vector(1.0, -1.0))
        sub_region.polygon.vertex_list.append(Vector(1.0, 2.0))
        sub_region.polygon.vertex_list.append(Vector(-2.0, 2.0))
        sub_region.polygon.vertex_list.append(Vector(-2.0, -1.0))
        hole = Polygon()
        hole.vertex_list.append(Vector(0.0, 0.0))
        hole.vertex_list.append(Vector(0.0, 1.0))
        hole.vertex_list.append(Vector(-1.0, 1.0))
        hole.vertex_list.append(Vector(-1.0, 0.0))
        sub_region.hole_list.append(hole)
        cut_region = CutRegion()
        cut_region.region = Region()
        cut_region.region.sub_region_list.append(sub_region)
        self.cut_region_list.append(cut_region)

        transform = AffineTransform()
        transform.Rotation(Vector(0.0, 0.0), math.pi / 4.0)
        for cut_region in self.cut_region_list:
            cut_region.Transform(transform)

    def Name(self):
        return 'Puzzle16'