# Puzzle13.py

import math

from Puzzle import Puzzle, CutRegion
from math2d_region import Region, SubRegion
from math2d_vector import Vector
from math2d_polygon import Polygon

class Puzzle13(Puzzle):
    def __init__(self):
        super().__init__()

        # This shape is almost a swashtica (I'm trying to avoid that for obvious reason) and
        # therefore only has rotational symmetry.
        sub_region = SubRegion()
        sub_region.polygon.vertex_list.append(Vector(1.0, 1.0))
        sub_region.polygon.vertex_list.append(Vector(1.0, 4.0))
        sub_region.polygon.vertex_list.append(Vector(-2.0, 4.0))
        sub_region.polygon.vertex_list.append(Vector(-2.0, 2.0))
        sub_region.polygon.vertex_list.append(Vector(-1.0, 2.0))
        sub_region.polygon.vertex_list.append(Vector(-1.0, 1.0))
        sub_region.polygon.vertex_list.append(Vector(-4.0, 1.0))
        sub_region.polygon.vertex_list.append(Vector(-4.0, -2.0))
        sub_region.polygon.vertex_list.append(Vector(-2.0, -2.0))
        sub_region.polygon.vertex_list.append(Vector(-2.0, -1.0))
        sub_region.polygon.vertex_list.append(Vector(-1.0, -1.0))
        sub_region.polygon.vertex_list.append(Vector(-1.0, -4.0))
        sub_region.polygon.vertex_list.append(Vector(2.0, -4.0))
        sub_region.polygon.vertex_list.append(Vector(2.0, -2.0))
        sub_region.polygon.vertex_list.append(Vector(1.0, -2.0))
        sub_region.polygon.vertex_list.append(Vector(1.0, -1.0))
        sub_region.polygon.vertex_list.append(Vector(4.0, -1.0))
        sub_region.polygon.vertex_list.append(Vector(4.0, 2.0))
        sub_region.polygon.vertex_list.append(Vector(2.0, 2.0))
        sub_region.polygon.vertex_list.append(Vector(2.0, 1.0))
        cut_region = CutRegion()
        cut_region.region = Region()
        cut_region.region.sub_region_list.append(sub_region)
        self.cut_region_list.append(cut_region)

        sub_region = SubRegion()
        sub_region.polygon.vertex_list.append(Vector(-3.0, 0.0))
        sub_region.polygon.vertex_list.append(Vector(-3.0, -3.0))
        sub_region.polygon.vertex_list.append(Vector(3.0, -3.0))
        sub_region.polygon.vertex_list.append(Vector(3.0, 0.0))
        hole = Polygon()
        hole.vertex_list.append(Vector(-1.0, -1.0))
        hole.vertex_list.append(Vector(-1.0, -2.0))
        hole.vertex_list.append(Vector(1.0, -2.0))
        hole.vertex_list.append(Vector(1.0, -1.0))
        sub_region.hole_list.append(hole)
        cut_region = CutRegion()
        cut_region.region = Region()
        cut_region.region.sub_region_list.append(sub_region)
        self.cut_region_list.append(cut_region)

    def Name(self):
        return 'Puzzle13'