# PuzzleGenerator.py

import os

from Puzzle import Puzzle
from Puzzle1 import Puzzle1

import argparse

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--puzzle', help='Which puzzle to generate.  All are generated if not given.', type=str)
    parser.add_argument('--puzzle_folder', help='Where to dump puzzle files.', type=str)
    
    args = parser.parse_args()
    
    puzzle_folder = args.puzzle_folder if args.puzzle_folder is not None else os.get_cwd()
    
    for puzzle_class in Puzzle.__subclasses__():
        puzzle = puzzle_class()
        if args.puzzle is not None and puzzle.Name() != args.puzzle:
            continue
        puzzle.Generate(puzzle_folder)