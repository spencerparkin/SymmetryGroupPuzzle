# Puzzle6.py

import math

from Puzzle import Puzzle, CutRegion
from math2d_affine_transform import AffineTransform
from math2d_vector import Vector
from math2d_polygon import Polygon

class Puzzle6(Puzzle):
    def __init__(self):
        super().__init__()

        cut_region = CutRegion()
        cut_region.GenerateRegularPolygon(4, 7.0 * math.sqrt(2.0))
        hole = Polygon()
        hole.MakeRegularPolygon(4, 5.0 * math.sqrt(2.0))
        cut_region.region.sub_region_list[0].hole_list.append(hole)
        transform = AffineTransform()
        transform.RigidBodyMotion(math.pi / 4.0, Vector(3.0, 3.0))
        cut_region.Transform(transform)
        self.cut_region_list.append(cut_region)

        cut_region = CutRegion()
        cut_region.GenerateRegularPolygon(4, 7.0 * math.sqrt(2.0))
        hole = Polygon()
        hole.MakeRegularPolygon(4, 5.0 * math.sqrt(2.0))
        cut_region.region.sub_region_list[0].hole_list.append(hole)
        transform = AffineTransform()
        transform.RigidBodyMotion(math.pi / 4.0, Vector(-3.0, -3.0))
        cut_region.Transform(transform)
        self.cut_region_list.append(cut_region)

    def Name(self):
        return 'Puzzle6'