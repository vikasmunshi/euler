#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 96: Su Doku.

Problem Statement:
    Su Doku (Japanese meaning number place) is the name given to a popular puzzle
    concept. Its origin is unclear, but credit must be attributed to Leonhard Euler
    who invented a similar, and much more difficult, puzzle idea called Latin Squares.
    The objective of Su Doku puzzles, however, is to replace the blanks (or zeros)
    in a 9 by 9 grid in such that each row, column, and 3 by 3 box contains each of
    the digits 1 to 9. Below is an example of a typical starting puzzle grid and its
    solution grid.

    A well constructed Su Doku puzzle has a unique solution and can be solved by
    logic, although it may be necessary to employ "guess and test" methods in order
    to eliminate options (there is much contested opinion over this). The complexity
    of the search determines the difficulty of the puzzle; the example above is
    considered easy because it can be solved by straight forward direct deduction.

    The 6K text file, sudoku.txt, contains fifty different Su Doku puzzles ranging
    in difficulty, but all with unique solutions (the first puzzle in the file is
    the example above).

    By solving all fifty puzzles find the sum of the 3-digit numbers found in the
    top left corner of each solution grid; for example, 483 is the 3-digit number
    found in the top left corner of the solution grid above.

Solution Approach:
    Use backtracking search with constraint propagation to solve each 9x9 Su Doku
    puzzle. Implement row, column, and box constraints efficiently. Sum the 3-digit
    numbers derived from solved puzzles. File parsing and multiple puzzle solving
    are straightforward. Algorithm complexity depends on branching but works well
    for standard puzzles.

Answer: 24702
URL: https://projecteuler.net/problem=96
"""
from __future__ import annotations

from concurrent.futures import Future, as_completed
from concurrent.futures.process import ProcessPoolExecutor
from copy import deepcopy
from typing import Any, Generator

from euler_solver.logger import logger
from euler_solver.maths.su_doku import print_grid, solve_sudoku
from euler_solver.setup import evaluate, get_text_file, register_solution, show_solution

euler_problem: int = 96
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'file_url': 'https://projecteuler.net/project/resources/p096_sudoku.txt'}}
]

Grid = list[list[int]]


def get_grids(file_url: str) -> Generator[Grid, None, None]:
    grid: Grid = []
    for line in get_text_file(url=file_url).splitlines(keepends=False):
        if line.startswith('Grid'):
            grid = []
        else:
            grid.append([int(d) for d in line.strip()])
        if len(grid) == 9:
            yield grid


def solve_one_grid(grid: Grid) -> int:
    assert solve_sudoku(grid), 'failed to solve grid'
    return int(''.join(map(str, grid[0][0:3])))


@register_solution(euler_problem=euler_problem, max_test_case=None)
def solve_su_doku_p0096_s0(*, file_url: str) -> int:
    s: int = 0
    if show_solution():
        for grid in get_grids(file_url=file_url):
            source_grid = deepcopy(grid)
            s += solve_one_grid(grid)
            print_grid(source_grid, grid)
    else:
        grids: tuple[Grid, ...] = tuple(get_grids(file_url=file_url))
        with ProcessPoolExecutor() as executor:
            futures: list[Future[int]] = [executor.submit(solve_one_grid, grid) for grid in grids]
        for completed in as_completed(futures):
            s += completed.result()
    return s


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))
