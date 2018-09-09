# PuzzleGenerator.py

import os
import sys

sys.path.append(r'C:\dev\pyMath2D')

from Puzzle import Puzzle
from Puzzle1 import Puzzle1
from Puzzle2 import Puzzle2
from Puzzle3 import Puzzle3
from Puzzle4 import Puzzle4
from Puzzle5 import Puzzle5
from Puzzle6 import Puzzle6
from Puzzle7 import Puzzle7
from Puzzle8 import Puzzle8
from Puzzle9 import Puzzle9
from Puzzle10 import Puzzle10
from Puzzle11 import Puzzle11
from Puzzle12 import Puzzle12
from Puzzle13 import Puzzle13
from Puzzle14 import Puzzle14
from Puzzle15 import Puzzle15
from Puzzle16 import Puzzle16
from Puzzle17 import Puzzle17

import argparse

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--puzzle', help='Which puzzle to generate.  All are generated if not given.', type=str)
    parser.add_argument('--puzzle_folder', help='Where to dump puzzle files.', type=str)
    parser.add_argument('--preview', help='This is used for debugging purposes.', type=str)
    parser.add_argument('--solve', help='If true, try to generate a solution to the puzzle in the form of a stab-chain.', action='store_true')
    
    args = parser.parse_args()
    
    puzzle_folder = args.puzzle_folder if args.puzzle_folder is not None else os.get_cwd()
    os.makedirs(puzzle_folder, exist_ok=True)
    
    for puzzle_class in Puzzle.__subclasses__():
        puzzle = puzzle_class()
        if args.puzzle is not None and puzzle.Name() != args.puzzle:
            continue
        print('=======================================================================')
        print('Processing: ' + puzzle.Name())
        puzzle.Generate(puzzle_folder, args.solve, args.preview)