# Puzzle3.py

import math

from Puzzle import Puzzle, CutRegion
from math2d_affine_transform import AffineTransform
from math2d_vector import Vector

class Puzzle3(Puzzle):
    def __init__(self):
        super().__init__()

        cut_region = CutRegion()
        cut_region.GenerateRegularPolygon(4, 3.0 * math.sqrt(2.0))
        transform = AffineTransform()
        transform.RigidBodyMotion(math.pi / 4.0, Vector(0.0, 0.0))
        cut_region.Transform(transform)
        self.cut_region_list.append(cut_region)

        cut_region = CutRegion()
        cut_region.GenerateRegularPolygon(4, math.sqrt(2.0))
        transform = AffineTransform()
        transform.RigidBodyMotion(math.pi / 4.0, Vector(-1.5, -1.5))
        cut_region.Transform(transform)
        self.cut_region_list.append(cut_region)

        cut_region = CutRegion()
        cut_region.GenerateRegularPolygon(4, math.sqrt(2.0))
        transform = AffineTransform()
        transform.RigidBodyMotion(math.pi / 4.0, Vector(3.0, 3.0))
        cut_region.Transform(transform)
        self.cut_region_list.append(cut_region)

    def Name(self):
        return 'Puzzle3'