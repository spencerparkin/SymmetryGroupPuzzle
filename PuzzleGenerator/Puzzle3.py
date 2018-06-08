# Puzzle3.py

import math

from Puzzle import Puzzle, CutRegion
from math2d_affine_transform import AffineTransform
from math2d_vector import Vector

class Puzzle3(Puzzle):
    def __init__(self):
        super().__init__()

        radius = 6.0

        cut_region = CutRegion()
        cut_region.GenerateRegularPolygon(4, radius)
        transform = AffineTransform()
        transform.Rotation(math.pi / 2.0)
        cut_region.Transform(transform)
        self.cut_region_list.append(cut_region)

        cut_region = CutRegion()
        cut_region.GenerateRegularPolygon(4, 2.0)
        transform = AffineTransform()
        transform.RigidBodyMotion(math.pi / 2.0, Vector(-2.0, -2.0))
        cut_region.Transform(transform)
        self.cut_region_list.append(cut_region)

        cut_region = CutRegion()
        cut_region.GenerateRegularPolygon(4, 2.0)
        transform = AffineTransform()
        transform.RigidBodyMotion(math.pi / 2.0, Vector(radius / math.sqrt(2.0), radius / math.sqrt(2.0)))
        cut_region.Transform(transform)
        self.cut_region_list.append(cut_region)

    def Name(self):
        return 'Puzzle3'