# Puzzle4.py

import math

from Puzzle import Puzzle, CutRegion
from math2d_affine_transform import AffineTransform
from math2d_vector import Vector
from math2d_polygon import Polygon

class Puzzle4(Puzzle):
    def __init__(self):
        super().__init__()

        cut_region = CutRegion()
        cut_region.GenerateRegularPolygon(5, 5.0)
        hole = Polygon()
        hole.MakeRegularPolygon(5, 4.0)
        cut_region.region.sub_region_list[0].hole_list.append(hole)
        self.cut_region_list.append(cut_region)

        cut_region = CutRegion()
        cut_region.GenerateRegularPolygon(5, 3.0)
        hole = Polygon()
        hole.MakeRegularPolygon(5, 2.0)
        cut_region.region.sub_region_list[0].hole_list.append(hole)
        self.cut_region_list.append(cut_region)

        # TODO: Add strip that connects them.  Before doing that, though,
        #       it looks like I need to figure out a bug in the empty cycle reader.

    def Name(self):
        return 'Puzzle4'