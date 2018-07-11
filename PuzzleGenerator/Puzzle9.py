# Puzzle9.py

import math

from Puzzle import Puzzle, CutRegion
from math2d_region import Region, SubRegion
from math2d_vector import Vector
from math2d_affine_transform import AffineTransform

class Puzzle9(Puzzle):
    def __init__(self):
        super().__init__()

        sub_region = SubRegion()
        sub_region.polygon.vertex_list.append(Vector(-1.0, -1.0))
        sub_region.polygon.vertex_list.append(Vector(1.0, -1.0))
        sub_region.polygon.vertex_list.append(Vector(1.0, 1.0))
        sub_region.polygon.vertex_list.append(Vector(-1.0, 1.0))
        cut_region = CutRegion()
        cut_region.region = Region()
        cut_region.region.sub_region_list.append(sub_region)
        self.cut_region_list.append(cut_region)

        sub_region = SubRegion()
        sub_region.polygon.vertex_list.append(Vector(-1.0, -1.0))
        sub_region.polygon.vertex_list.append(Vector(1.0, -1.0))
        sub_region.polygon.vertex_list.append(Vector(1.0, 1.0))
        sub_region.polygon.vertex_list.append(Vector(-1.0, 1.0))
        cut_region = CutRegion()
        cut_region.region = Region()
        cut_region.region.sub_region_list.append(sub_region)
        transform = AffineTransform()
        transform.Translation(Vector(2.0, 0.0))
        cut_region.Transform(transform)
        self.cut_region_list.append(cut_region)

        sub_region = SubRegion()
        sub_region.polygon.vertex_list.append(Vector(-1.0, -1.0))
        sub_region.polygon.vertex_list.append(Vector(1.0, -1.0))
        sub_region.polygon.vertex_list.append(Vector(1.0, 1.0))
        sub_region.polygon.vertex_list.append(Vector(-1.0, 1.0))
        cut_region = CutRegion()
        cut_region.region = Region()
        cut_region.region.sub_region_list.append(sub_region)
        transform = AffineTransform()
        transform.Translation(Vector(-2.0, 0.0))
        cut_region.Transform(transform)
        self.cut_region_list.append(cut_region)

        sub_region = SubRegion()
        sub_region.polygon.vertex_list.append(Vector(-1.0, -1.0))
        sub_region.polygon.vertex_list.append(Vector(1.0, -1.0))
        sub_region.polygon.vertex_list.append(Vector(1.0, 1.0))
        sub_region.polygon.vertex_list.append(Vector(-1.0, 1.0))
        cut_region = CutRegion()
        cut_region.region = Region()
        cut_region.region.sub_region_list.append(sub_region)
        transform = AffineTransform()
        transform.Translation(Vector(2.0, -2.0))
        cut_region.Transform(transform)
        self.cut_region_list.append(cut_region)

        sub_region = SubRegion()
        sub_region.polygon.vertex_list.append(Vector(-1.0, -1.0))
        sub_region.polygon.vertex_list.append(Vector(1.0, -1.0))
        sub_region.polygon.vertex_list.append(Vector(1.0, 1.0))
        sub_region.polygon.vertex_list.append(Vector(-1.0, 1.0))
        cut_region = CutRegion()
        cut_region.region = Region()
        cut_region.region.sub_region_list.append(sub_region)
        transform = AffineTransform()
        transform.Translation(Vector(-2.0, 2.0))
        cut_region.Transform(transform)
        self.cut_region_list.append(cut_region)

        sub_region = SubRegion()
        sub_region.polygon.vertex_list.append(Vector(-3.0, 0.0))
        sub_region.polygon.vertex_list.append(Vector(3.0, 0.0))
        sub_region.polygon.vertex_list.append(Vector(3.0, -6.0))
        sub_region.polygon.vertex_list.append(Vector(5.0, -6.0))
        sub_region.polygon.vertex_list.append(Vector(5.0, 2.0))
        sub_region.polygon.vertex_list.append(Vector(-3.0, 2.0))
        cut_region = CutRegion()
        cut_region.region = Region()
        cut_region.region.sub_region_list.append(sub_region)
        self.cut_region_list.append(cut_region)

        sub_region = SubRegion()
        sub_region.polygon.vertex_list.append(Vector(-3.0, 0.0))
        sub_region.polygon.vertex_list.append(Vector(-3.0, 6.0))
        sub_region.polygon.vertex_list.append(Vector(-5.0, 6.0))
        sub_region.polygon.vertex_list.append(Vector(-5.0, -2.0))
        sub_region.polygon.vertex_list.append(Vector(3.0, -2.0))
        sub_region.polygon.vertex_list.append(Vector(3.0, 0.0))
        cut_region = CutRegion()
        cut_region.region = Region()
        cut_region.region.sub_region_list.append(sub_region)
        self.cut_region_list.append(cut_region)

    def Name(self):
        return 'Puzzle9'