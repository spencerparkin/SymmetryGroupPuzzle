# Level.py

import math

from Math.Vector import Vector
from Puzzle.Puzzle import Cutter, Puzzle

def MakePuzzle(level):
    cutter_list = []
    if level == 1:
        triangleA = Cutter()
        triangleA.MakeRegularPolygon(3, Vector(3.0, 0.0), 5.0, math.pi / 3.0)
        cutter_list.append(triangleA)
        triangleB = Cutter()
        triangleB.MakeRegularPolygon(3, Vector(-3.0, 0.0), 5.0, 0.0)
        cutter_list.append(triangleB)
    elif level == 2:
        pass
    elif level == 3:
        pass
    puzzle = Puzzle(cutter_list)
    return puzzle