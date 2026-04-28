#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Migrated from
    euler_solver/solutions/solutions_0001_0100/solution_0096/p0096.py :: solve_su_doku_p0096_s0.

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
URL: https://projecteuler.net/problem=96"""
from __future__ import annotations

import sys
from concurrent.futures import Future, as_completed
from concurrent.futures.process import ProcessPoolExecutor
from copy import deepcopy
from pathlib import Path
from typing import Any, Generator

Grid = list[list[int]]


def get_text_file(url: str) -> str:
    """ Return the contents of a file from the 'resources' directory. """
    local_filename: str = 'resources' + '/' + url.split('/')[-1].split('?')[0]
    return (Path(__file__).parent / local_filename).read_text()


def get_grids(file_url: str) -> Generator[Grid, None, None]:
    grid: Grid = []
    for line in get_text_file(url=file_url).splitlines(keepends=False):
        if line.startswith('Grid'):
            grid = []
        else:
            grid.append([int(d) for d in line.strip()])
        if len(grid) == 9:
            yield grid


def is_valid_sudoku_grid(grid: Grid) -> bool:
    if len(grid) != 9:
        return False
    for row in grid:
        if len(row) != 9:
            return False
    return True


def update_possibilities(empty_cells: list[tuple[int, int, set[int]]], row: int, col: int, number: int
                         ) -> list[tuple[int, int, set[int]]]:
    updated_cells = []
    for r, c, possibilities in empty_cells:
        if r == row or c == col or (r // 3 == row // 3 and c // 3 == col // 3):
            new_possibilities = possibilities - {number} if number in possibilities else possibilities
            updated_cells.append((r, c, new_possibilities))
        else:
            updated_cells.append((r, c, possibilities))
    return updated_cells


def solve_backtracking(grid: Grid, empty_cells: list[tuple[int, int, set[int]]]) -> bool:
    if not empty_cells:
        return True
    empty_cells.sort(key=lambda c: len(c[2]))
    row, col, possibilities = empty_cells.pop(0)
    for possibility in possibilities:
        grid[row][col] = possibility
        updated_cells = update_possibilities(empty_cells, row, col, possibility)
        if solve_backtracking(grid, updated_cells):
            return True
        grid[row][col] = 0
    empty_cells.insert(0, (row, col, possibilities))
    return False


def get_values_in_square(grid: Grid, row: int, col: int) -> Generator[int, None, None]:
    row -= row % 3
    col -= col % 3
    for i in range(3):
        for j in range(3):
            yield grid[row + i][col + j]


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


def get_all_empty_cells_with_possibilities(grid: Grid) -> list[tuple[int, int, set[int]]]:
    empty_cells = []
    for row in range(9):
        for col in range(9):
            if grid[row][col] == 0:
                possibilities = get_possibilities(grid, row, col)
                empty_cells.append((row, col, possibilities))
    return empty_cells


def solve_sudoku(grid: Grid) -> bool:
    assert is_valid_sudoku_grid(grid), f'Invalid Sudoku grid {grid}'
    empty_cells = get_all_empty_cells_with_possibilities(grid)
    return solve_backtracking(grid, empty_cells)


def solve_one_grid(grid: Grid) -> int:
    assert solve_sudoku(grid), 'failed to solve grid'
    return int(''.join(map(str, grid[0][0:3])))


def show_solution() -> bool:
    return '--show' in sys.argv


def print_e(*msg: Any, **kwargs: str) -> None:
    print(*msg, **kwargs, file=sys.stderr)  # type: ignore[call-overload]


def print_grid(grid_0: Grid, grid_1: Grid) -> None:
    print_e('     Unsolved Grid       ⟶⟶⟶      Solved Grid        ')
    print_e('┌───────┬───────┬───────┐   ┌───────┬───────┬───────┐')
    for rb in range(3):
        if rb > 0:
            print_e('├───────┼───────┼───────┤   ├───────┼───────┼───────┤')
        for r in range(3):
            for cb in range(3):
                print_e('│', end='')
                for c in range(3):
                    print_e(' ', end='')
                    print_e(grid_0[rb * 3 + r][cb * 3 + c] or ' ', end='')
                print_e(' ', end='')
            print_e('│⟶⟶⟶' if rb == 1 and r == 1 else '│   ', end='')
            for cb in range(3):
                print_e('│', end='')
                for c in range(3):
                    print_e(' ', end='')
                    print_e(grid_1[rb * 3 + r][cb * 3 + c] or ' ', end='')
                print_e(' ', end='')
            print_e('│ ')
    print_e('└───────┴───────┴───────┘   └───────┴───────┴───────┘')
    print_e(' ─────────────────────────────────────────────────── ')


def solve(*, file_url: str) -> int:
    grids: tuple[Grid, ...] = tuple(get_grids(file_url=file_url))
    s: int = 0
    if show_solution():
        for grid in grids:
            source_grid = deepcopy(grid)
            s += solve_one_grid(grid)
            print_grid(source_grid, grid)
    else:
        with ProcessPoolExecutor() as executor:
            futures: list[Future[int]] = [executor.submit(solve_one_grid, grid) for grid in grids]
        for completed in as_completed(futures):
            s += completed.result()
    return s


if __name__ == '__main__':
    sys.setrecursionlimit(10 ** 6)
    print(solve(file_url=str(sys.argv[1])))
