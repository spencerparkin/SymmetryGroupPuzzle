# Puzzle12.py

import math

from Puzzle import Puzzle, CutRegion
from math2d_region import Region, SubRegion
from math2d_vector import Vector

class Puzzle12(Puzzle):
    def __init__(self):
        super().__init__()

        # It's amazing how hard or easy 2 overlapping squares is.
        # It depends on _how_ the squares overlap!

        sub_region = SubRegion()
        sub_region.polygon.vertex_list.append(Vector(0.0, 0.0))
        sub_region.polygon.vertex_list.append(Vector(3.0, 0.0))
        sub_region.polygon.vertex_list.append(Vector(3.0, 3.0))
        sub_region.polygon.vertex_list.append(Vector(0.0, 3.0))
        cut_region = CutRegion()
        cut_region.region = Region()
        cut_region.region.sub_region_list.append(sub_region)
        self.cut_region_list.append(cut_region)

        sub_region = SubRegion()
        sub_region.polygon.vertex_list.append(Vector(2.0, 1.0))
        sub_region.polygon.vertex_list.append(Vector(5.0, 1.0))
        sub_region.polygon.vertex_list.append(Vector(5.0, 4.0))
        sub_region.polygon.vertex_list.append(Vector(2.0, 4.0))
        cut_region = CutRegion()
        cut_region.region = Region()
        cut_region.region.sub_region_list.append(sub_region)
        self.cut_region_list.append(cut_region)

    def Name(self):
        return 'Puzzle12'
    
    def PopulatePointCloudForPermutationGroup(self, cloud, graph):
        for x in range(0, 5):
            for y in range(0, 4):
                if (x < 2 and y == 3) or (x > 2 and y == 0):
                    continue
                center = Vector(x + 0.5, y + 0.5)
                cloud.Add(center + Vector(-0.3, -0.3))
                cloud.Add(center + Vector(0.3, -0.3))
                cloud.Add(center + Vector(0.3, 0.3))
                cloud.Add(center + Vector(-0.3, 0.3))
        return True