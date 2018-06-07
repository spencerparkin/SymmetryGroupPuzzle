# Puzzle1.py

import math

from Puzzle import Puzzle, CutRegion
from math2d_affine_transform import AffineTransform
from math2d_vector import Vector

class Puzzle1(Puzzle):
    def __init__(self):
        super().__init__()
        
        cut_region = CutRegion()
        cut_region.GenerateRegularPolygon(3, 4.0)
        transform = AffineTransform()
        transform.Translation(Vector(-2.0, 0.0))
        cut_region.Transform(transform)
        self.cut_region_list.append(cut_region)

        cut_region = CutRegion()
        cut_region.GenerateRegularPolygon(3, 4.0)
        transform = AffineTransform()
        transform.Rotation()
        transform.RigidBodyMotion(math.pi / 3.0, Vector(2.0, 0.0))
        cut_region.Transform(transform)
        self.cut_shape_list.append(cut_region)
    
    def Name(self):
        return 'Puzzle1'