# Puzzle11.py

import math

from Puzzle import Puzzle, CutRegion
from math2d_region import Region, SubRegion
from math2d_vector import Vector

class Puzzle11(Puzzle):
    def __init__(self):
        super().__init__()

        radius = 7.0

        x = radius * math.cos(math.pi / 3.0)
        y = radius * math.sin(math.pi / 3.0)

        cut_region = CutRegion()
        cut_region.GenerateRegularPolygon(6, radius)
        self.cut_region_list.append(cut_region)

        sub_region = SubRegion()
        sub_region.polygon.vertex_list.append(Vector(radius, 0.0))
        sub_region.polygon.vertex_list.append(Vector(x, y))
        sub_region.polygon.vertex_list.append(Vector(x, -y))
        cut_region = CutRegion()
        cut_region.region = Region()
        cut_region.region.sub_region_list.append(sub_region)
        self.cut_region_list.append(cut_region)

        sub_region = SubRegion()
        sub_region.polygon.vertex_list.append(Vector(radius, 0.0))
        sub_region.polygon.vertex_list.append(Vector(x, y))
        sub_region.polygon.vertex_list.append(Vector(-x, y))
        sub_region.polygon.vertex_list.append(Vector(-radius, 0.0))
        cut_region = CutRegion()
        cut_region.region = Region()
        cut_region.region.sub_region_list.append(sub_region)
        self.cut_region_list.append(cut_region)

    def Name(self):
        return 'Puzzle11'