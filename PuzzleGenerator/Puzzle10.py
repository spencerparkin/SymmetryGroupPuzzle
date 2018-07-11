# Puzzle10.py

import math

from Puzzle import Puzzle, CutRegion
from math2d_region import Region, SubRegion
from math2d_vector import Vector

class Puzzle10(Puzzle):
    def __init__(self):
        super().__init__()

        # TODO: This shape will have reflection symmetries that the interface can't access.  Fix it.  How?
        cut_region = CutRegion()
        cut_region.region = Region()
        sub_region = SubRegion()
        sub_region.polygon.vertex_list.append(Vector(3.0, 3.0))
        sub_region.polygon.vertex_list.append(Vector(5.0, 3.0))
        sub_region.polygon.vertex_list.append(Vector(3.0, 5.0))
        cut_region.region.sub_region_list.append(sub_region)
        sub_region = SubRegion()
        sub_region.polygon.vertex_list.append(Vector(-3.0, 3.0))
        sub_region.polygon.vertex_list.append(Vector(-3.0, 5.0))
        sub_region.polygon.vertex_list.append(Vector(-5.0, 3.0))
        cut_region.region.sub_region_list.append(sub_region)
        sub_region = SubRegion()
        sub_region.polygon.vertex_list.append(Vector(-3.0, -3.0))
        sub_region.polygon.vertex_list.append(Vector(-5.0, -3.0))
        sub_region.polygon.vertex_list.append(Vector(-3.0, -5.0))
        cut_region.region.sub_region_list.append(sub_region)
        sub_region = SubRegion()
        sub_region.polygon.vertex_list.append(Vector(3.0, -3.0))
        sub_region.polygon.vertex_list.append(Vector(3.0, -5.0))
        sub_region.polygon.vertex_list.append(Vector(5.0, -3.0))
        cut_region.region.sub_region_list.append(sub_region)
        self.cut_region_list.append(cut_region)

        sub_region = SubRegion()
        sub_region.polygon.vertex_list.append(Vector(-4.5, -4.5))
        sub_region.polygon.vertex_list.append(Vector(1.5, -1.5))
        sub_region.polygon.vertex_list.append(Vector(4.5, 4.5))
        sub_region.polygon.vertex_list.append(Vector(-1.5, 1.5))
        cut_region = CutRegion()
        cut_region.region = Region()
        cut_region.region.sub_region_list.append(sub_region)
        self.cut_region_list.append(cut_region)

        sub_region = SubRegion()
        sub_region.polygon.vertex_list.append(Vector(4.5, -4.5))
        sub_region.polygon.vertex_list.append(Vector(1.5, 1.5))
        sub_region.polygon.vertex_list.append(Vector(-4.5, 4.5))
        sub_region.polygon.vertex_list.append(Vector(-1.5, -1.5))
        cut_region = CutRegion()
        cut_region.region = Region()
        cut_region.region.sub_region_list.append(sub_region)
        self.cut_region_list.append(cut_region)

    def Name(self):
        return 'Puzzle10'