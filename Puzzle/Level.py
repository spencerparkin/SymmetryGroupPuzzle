# Level.py

import math

from Math.Vector import Vector
from Math.Rectangle import Rectangle
from Puzzle.Puzzle import Cutter, Puzzle

def MakePuzzle(level):
    window = None
    cutter_list = []
    if level == 1:
        triangleA = Cutter()
        triangleA.MakeRegularPolygon(3, Vector(3.0, 0.0), 5.0, math.pi / 3.0)
        cutter_list.append(triangleA)
        triangleB = Cutter()
        triangleB.MakeRegularPolygon(3, Vector(-3.0, 0.0), 5.0, 0.0)
        cutter_list.append(triangleB)
        window = Rectangle(Vector(-8.0, -8.0), Vector(8.0, 8.0))
    elif level == 2:
        pass
    elif level == 3:
        pass
    puzzle = Puzzle(cutter_list, window)
    return puzzle