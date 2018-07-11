# Puzzle13.py

import math

from Puzzle import Puzzle, CutRegion
from math2d_region import Region, SubRegion
from math2d_vector import Vector

class Puzzle13(Puzzle):
    def __init__(self):
        super().__init__()

        # TODO: The swashtica haw rotational symmetry, but no reflection symmetry.
        #       So we'll fail to generate it's symmetries.  Fix that.
        sub_region = SubRegion()
        sub_region.polygon.vertex_list.append(Vector())
        cut_region = CutRegion()
        cut_region.region = Region()
        cut_region.region.sub_region_list.append(sub_region)
        self.cut_region_list.append(cut_region)

    def Name(self):
        return 'Puzzle13'