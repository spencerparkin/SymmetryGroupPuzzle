# Puzzle15.py

import math

from Puzzle import Puzzle, CutRegion
from math2d_region import Region, SubRegion
from math2d_vector import Vector
from math2d_polygon import Polygon
from math2d_affine_transform import AffineTransform

class Puzzle15(Puzzle):
    def __init__(self):
        super().__init__()

        cut_region = CutRegion()
        cut_region.GenerateRegularPolygon(8, 1.0)
        self.cut_region_list.append(cut_region)

        cut_region = CutRegion()
        cut_region.GenerateRegularPolygon(8, 2.0)
        self.cut_region_list.append(cut_region)

        cut_region = CutRegion()
        cut_region.GenerateRegularPolygon(8, 3.0)
        self.cut_region_list.append(cut_region)

        cut_region = CutRegion()
        cut_region.GenerateRegularPolygon(8, 4.0)
        self.cut_region_list.append(cut_region)

        sub_region = SubRegion()
        sub_region.polygon.vertex_list.append(Vector(0.0, 0.0))
        sub_region.polygon.vertex_list.append(Vector(4.0, 0.0))
        sub_region.polygon.vertex_list.append(Vector(4.0 * math.cos(math.pi / 4.0), 4.0 * math.sin(math.pi / 4)))
        cut_region = CutRegion()
        cut_region.region = Region()
        cut_region.region.sub_region_list.append(sub_region)
        self.cut_region_list.append(cut_region)

        transform = AffineTransform()
        transform.Rotation(Vector(0.0, 0.0), math.pi / 2.0 - math.pi / 8.0)
        for cut_region in self.cut_region_list:
            cut_region.Transform(transform)

    def Name(self):
        return 'Puzzle15'