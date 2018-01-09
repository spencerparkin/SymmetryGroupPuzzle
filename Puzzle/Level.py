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
        x = 2.0
        y = -4.0
        pentagonA = Cutter()
        pentagonA.MakeRegularPolygon(5, Vector(x, y), 5.0, 0.0)
        cutter_list.append(pentagonA)
        d = 7.0
        a = 2.0 * math.pi / 5.0
        pentagonB = Cutter()
        pentagonB.MakeRegularPolygon(5, Vector(x, y) + Vector().Polar(d, a), 5.0, -math.pi / 5.0)
        cutter_list.append(pentagonB)
        a = 4.0 * math.pi / 5.0
        pentagonC = Cutter()
        pentagonC.MakeRegularPolygon(5, Vector(x, y) + Vector().Polar(d, a), 3.0, -math.pi / 5.0)
        cutter_list.append(pentagonC)
    elif level == 3:
        squareA = Cutter()
        squareA.MakeRegularPolygon(4, Vector(0.0, 0.0), 5.0)
        cutter_list.append(squareA)
        squareB = Cutter()
        squareB.MakeRegularPolygon(4, Vector(-2.5, 2.5), 2.0)
        cutter_list.append(squareB)
    elif level == 4:
        squareA = Cutter()
        squareA.MakeRegularPolygon(4, Vector(0.0, 0.0), 5.0, math.pi / 4.0)
        cutter_list.append(squareA)
        squareB = Cutter()
        squareB.MakeRegularPolygon(4, Vector(-2.5, 2.5), 2.0, math.pi / 4.0)
        cutter_list.append(squareB)
    elif level == -1:
        # Here is an example of a puzzle that the puzzle engine can't handle,
        # because it can't handle general topologies.  Admittedly, this is
        # one place where my previous attempt to implement this puzzle game
        # was actually better than this one, because my original implementation,
        # I believe, could handle general topologies provided its initial
        # triangle mesh was dense enough.  Of course, the big problem with my
        # previous implementation is that it was way too heavy on the triangles.
        squareA = Cutter()
        squareA.MakeRegularPolygon(4, Vector(0.0, 0.0), 5.0, math.pi / 4.0)
        cutter_list.append(squareA)
        squareB = Cutter()
        squareB.MakeRegularPolygon(4, Vector(-2.5, 2.5), 1.0, math.pi / 4.0)
        cutter_list.append(squareB)
    elif level == 5:
        # TODO: This one should be supported by the puzzle engine, but I've
        #       noticed that it has a bug.  One of the cutters doesn't appear
        #       to always cut and capture a corner of the big square.  :(
        squareA = Cutter()
        squareA.MakeRegularPolygon(4, Vector(0.0, 0.0), 5.0)
        cutter_list.append(squareA)
        squareB = Cutter()
        squareB.MakeRegularPolygon(4, Vector(3.0, 0.0), 2.0)
        cutter_list.append(squareB)
        squareC = Cutter()
        squareC.MakeRegularPolygon(4, Vector(0.0, 5.0), 2.0)
        cutter_list.append(squareC)
    puzzle = Puzzle(cutter_list)
    return puzzle