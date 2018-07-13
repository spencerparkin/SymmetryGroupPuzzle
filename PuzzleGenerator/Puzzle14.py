# Puzzle14.py

import math

from Puzzle import Puzzle, CutRegion
from math2d_region import Region, SubRegion
from math2d_vector import Vector
from math2d_polygon import Polygon

class Puzzle14(Puzzle):
    def __init__(self):
        super().__init__()

        sub_region = SubRegion()
        sub_region.polygon.vertex_list.append(Vector(-1.0, -math.sqrt(3.0)))
        sub_region.polygon.vertex_list.append(Vector(3.0, -math.sqrt(3.0)))
        sub_region.polygon.vertex_list.append(Vector(1.0, math.sqrt(3.0)))
        cut_region = CutRegion()
        cut_region.region = Region()
        cut_region.region.sub_region_list.append(sub_region)
        self.cut_region_list.append(cut_region)

        sub_region = SubRegion()
        sub_region.polygon.vertex_list.append(Vector(1.0, math.sqrt(3.0)))
        sub_region.polygon.vertex_list.append(Vector(-3.0, math.sqrt(3.0)))
        sub_region.polygon.vertex_list.append(Vector(-1.0, -math.sqrt(3.0)))
        cut_region = CutRegion()
        cut_region.region = Region()
        cut_region.region.sub_region_list.append(sub_region)
        self.cut_region_list.append(cut_region)

        # A reflection symmetry of this rectangle won't be accessible.  Hmmmm...
        sub_region = SubRegion()
        sub_region.polygon.vertex_list.append(Vector(-3.0, math.sqrt(3.0)))
        sub_region.polygon.vertex_list.append(Vector(-3.0, -math.sqrt(3.0)))
        sub_region.polygon.vertex_list.append(Vector(3.0, -math.sqrt(3.0)))
        sub_region.polygon.vertex_list.append(Vector(3.0, math.sqrt(3.0)))
        cut_region = CutRegion()
        cut_region.region = Region()
        cut_region.region.sub_region_list.append(sub_region)
        self.cut_region_list.append(cut_region)

    def Name(self):
        return 'Puzzle14'