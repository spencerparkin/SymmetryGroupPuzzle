# Level.py

import math

from Math.Vector import Vector
from Puzzle.Puzzle import Cutter, Puzzle

def MakePuzzle(level):
    cutter_list = []
    if level == 0:
        triangleA = Cutter()
        triangleA.MakeRegularPolygon(3, Vector(3.0, 0.0), 5.0, math.pi / 3.0)
        cutter_list.append(triangleA)
        triangleB = Cutter()
        triangleB.MakeRegularPolygon(3, Vector(-3.0, 0.0), 5.0, 0.0)
        cutter_list.append(triangleB)
    elif level == 1:
        squareA = Cutter()
        squareA.MakeRegularPolygon(4, Vector(-2.0, 2.0), 3.0 * math.sqrt(2.0), math.pi / 4.0)
        cutter_list.append(squareA)
        squareB = Cutter()
        squareB.MakeRegularPolygon(4, Vector(2.0, -2.0), 3.0 * math.sqrt(2.0), math.pi / 4.0)
        cutter_list.append(squareB)
    elif level == 2:
        pass
    puzzle = Puzzle(cutter_list)
    return puzzle