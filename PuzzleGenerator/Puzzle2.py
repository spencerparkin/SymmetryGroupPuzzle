# Puzzle2.py

from Puzzle import Puzzle, CutRegion
from math2d_affine_transform import AffineTransform
from math2d_vector import Vector

class Puzzle2(Puzzle):
    def __init__(self):
        super().__init__()

        cut_region = CutRegion()
        cut_region.GenerateRegularPolygon(4, 2.0)
        self.cut_region_list.append(cut_region)

        cut_region = CutRegion()
        cut_region.GenerateRegularPolygon(4, 3.5)
        transform = AffineTransform()
        transform.RigidBodyMotion(0.0, Vector(-4.0, 0.0))
        cut_region.Transform(transform)
        self.cut_region_list.append(cut_region)

        cut_region = CutRegion()
        cut_region.GenerateRegularPolygon(4, 3.0)
        transform = AffineTransform()
        transform.RigidBodyMotion(0.0, Vector(4.0, 0.0))
        cut_region.Transform(transform)
        self.cut_region_list.append(cut_region)

    def Name(self):
        return 'Puzzle2'