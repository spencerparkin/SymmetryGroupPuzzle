# Puzzle8.py

import math

from Puzzle import Puzzle, CutRegion
from math2d_region import Region, SubRegion
from math2d_vector import Vector

class Puzzle8(Puzzle):
    def __init__(self):
        super().__init__()

        cut_region = CutRegion()
        cut_region.GenerateRegularPolygon(4, 2.0)
        self.cut_region_list.append(cut_region)

        sub_region = SubRegion()
        sub_region.polygon.vertex_list.append(Vector(1.0, 0.0))
        sub_region.polygon.vertex_list.append(Vector(4.0, 0.0))
        sub_region.polygon.vertex_list.append(Vector(2.5, math.sqrt(3.0) * 3.0 / 2.0))
        cut_region = CutRegion()
        cut_region.region = Region()
        cut_region.region.sub_region_list.append(sub_region)
        self.cut_region_list.append(cut_region)

        # This shape has reflection symmetry, but no rotational symmetry.
        sub_region = SubRegion()
        sub_region.polygon.vertex_list.append(Vector(-1.0, 0.0))
        sub_region.polygon.vertex_list.append(Vector(-1.0, 2.0))
        sub_region.polygon.vertex_list.append(Vector(-3.0, 0.0))
        cut_region = CutRegion()
        cut_region.region = Region()
        cut_region.region.sub_region_list.append(sub_region)
        self.cut_region_list.append(cut_region)

    def Name(self):
        return 'Puzzle8'