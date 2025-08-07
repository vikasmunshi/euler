#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
  Project Euler Problem 96: Su Doku.

  Problem Statement:
    Su Doku (Japanese meaning number place) is the name given to a popular
    puzzle concept. Its origin is unclear, but credit must be attributed to
    Leonhard Euler who invented a similar, and much more difficult, puzzle
    idea called Latin Squares. The objective of Su Doku puzzles, however, is
    to replace the blanks (or zeros) in a 9 by 9 grid in such that each row,
    column, and 3 by 3 box contains each of the digits 1 to 9. Below is an
    example of a typical starting puzzle grid and its solution grid.

    A well constructed Su Doku puzzle has a unique solution and can be solved
    by logic, although it may be necessary to employ "guess and test" methods
    in order to eliminate options (there is much contested opinion over
    this). The complexity of the search determines the difficulty of the
    puzzle; the example above is considered easy because it can be solved by
    straight forward direct deduction.

    The 6K text file, sudoku.txt (right click and 'Save Link/Target As...'),
    contains fifty different Su Doku puzzles ranging in difficulty, but all
    with unique solutions (the first puzzle in the file is the example above).

    By solving all fifty puzzles find the sum of the 3-digit numbers found
    in the top left corner of each solution grid; for example, 483 is the
    3-digit number found in the top left corner of the solution grid above.

  Solution Approach:
    To solve these Su Doku puzzles, implement a backtracking algorithm that
    fills in the blanks by trying possible digits and checking the constraints
    of rows, columns, and 3x3 boxes. The solver should proceed by placing a
    number in an empty cell and then recursively attempting to solve the rest
    of the puzzle.

    Constraint propagation techniques like elimination and only-choice can be
    used to reduce the search space. Each puzzle's uniqueness ensures that once
    a correct path is chosen, no ambiguity remains. Summing the specified 3-digit
    numbers from each solution requires parsing the result grids after solving
    each puzzle in the provided input file.

  Test Cases:
    main:
      file_url=https://projecteuler.net/project/resources/p096_sudoku.txt,
      answer=24702.


  Answer: 24702
  URL: https://projecteuler.net/problem=96
"""
from __future__ import annotations

from copy import deepcopy
from typing import Generator

from euler.logger import logger
from euler.setup import TestCaseCategory, evaluate, register_solution, show_solution
from euler.setup.cached_requests import get_text_file

Grid = list[list[int]]


def fill_in(grid: Grid, row: int, col: int) -> bool:
    if row >= 9:
        return True
    if grid[row][col]:
        return fill_in(grid, row + 1 if col == 8 else row, (col + 1) % 9)
    possibilities = get_possibilities(grid, row, col)
    for possibility in possibilities:
        grid[row][col] = possibility
        if fill_in(grid, row + 1 if col == 8 else row, (col + 1) % 9):
            return True
        grid[row][col] = 0
    return False


def get_grids(file_url: str) -> Generator[Grid, None, None]:
    grid: Grid = []
    for line in get_text_file(url=file_url).splitlines(keepends=False):
        if line.startswith('Grid'):
            grid = []
        else:
            grid.append([int(d) for d in line.strip()])
        if len(grid) == 9:
            yield grid


def get_possibilities(grid: Grid, row: int, col: int) -> set[int]:
    if grid[row][col]:
        return set()
    possible = set(range(1, 10))
    for c in range(9):
        possible.discard(grid[row][c])
    for r in range(9):
        possible.discard(grid[r][col])
    for elem in get_values_in_square(grid, row, col):
        possible.discard(elem)
    return possible


def get_values_in_square(grid: Grid, row: int, col: int) -> Generator[int, None, None]:
    row -= row % 3
    col -= col % 3
    for i in range(3):
        for j in range(3):
            yield grid[row + i][col + j]


def print_grid(grid_0: Grid, grid_1: Grid) -> None:
    print('     Unsolved Grid       ⟶⟶⟶      Solved Grid        ')
    print('┌───────┬───────┬───────┐   ┌───────┬───────┬───────┐')
    for rb in range(3):
        if rb > 0:
            print('├───────┼───────┼───────┤   ├───────┼───────┼───────┤')
        for r in range(3):
            for cb in range(3):
                print('│', end='')
                for c in range(3):
                    print(' ', end='')
                    print(grid_0[rb * 3 + r][cb * 3 + c] or ' ', end='')
                print(' ', end='')
            print('│⟶⟶⟶' if rb == 1 and r == 1 else '│   ', end='')
            for cb in range(3):
                print('│', end='')
                for c in range(3):
                    print(' ', end='')
                    print(grid_1[rb * 3 + r][cb * 3 + c] or ' ', end='')
                print(' ', end='')
            print('│ ')
    print('└───────┴───────┴───────┘   └───────┴───────┴───────┘')
    print(' ─────────────────────────────────────────────────── ')


@register_solution(euler_problem=96, test_case_category=TestCaseCategory.EXTENDED)
def su_doku(*, file_url: str) -> int:
    s: int = 0
    if show_solution():
        for grid in get_grids(file_url=file_url):
            source_grid = deepcopy(grid)
            assert fill_in(grid, 0, 0), 'Failed to solve grid'
            s += int(''.join(map(str, grid[0][0:3])))
            print_grid(source_grid, grid)
    else:
        for grid in get_grids(file_url=file_url):
            assert fill_in(grid, 0, 0), 'Failed to solve grid'
            s += int(''.join(map(str, grid[0][0:3])))
    return s


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=96, time_out_in_seconds=300, mode='evaluate'))
