# Puzzle5.py

import math

from Puzzle import Puzzle, CutRegion
from math2d_affine_transform import AffineTransform
from math2d_vector import Vector
from math2d_polygon import Polygon

class Puzzle5(Puzzle):
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

        # This is almost like puzzle 4, but with a subtle difference.
        cut_region = CutRegion()
        cut_region.GenerateRectangle(5.0, 1.0)
        transform = AffineTransform()
        transform.translation = Vector(-3.0, 0.0)
        cut_region.Transform(transform)
        self.cut_region_list.append(cut_region)

    def Name(self):
        return 'Puzzle5'