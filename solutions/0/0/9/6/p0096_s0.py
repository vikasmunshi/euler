#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 96: Su Doku [Level 5]. """
from __future__ import annotations

import copy
import typing

from solver.runners import runner

Grid = list[list[int]]


def get_grids(file_url: str) -> typing.Generator[Grid, None, None]:
    """Yield each 9x9 puzzle from the resource file, skipping the 'Grid NN' labels."""
    grid: Grid = []
    for line in runner.get_text_file(file_url).splitlines(keepends=False):
        if line.startswith("Grid"):
            grid = []
        else:
            grid.append([int(d) for d in line.strip()])
        if len(grid) == 9:
            yield grid


def get_values_in_square(grid: Grid, row: int, col: int) -> typing.Generator[int, None, None]:
    """Yield the nine values of the 3x3 box containing (row, col)."""
    row -= row % 3
    col -= col % 3
    for i in range(3):
        for j in range(3):
            yield grid[row + i][col + j]


def get_possibilities(grid: Grid, row: int, col: int) -> set[int]:
    """Candidates for an empty cell: {1..9} minus its row, column, and box digits."""
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
    """Build the working set once: a (row, col, candidates) triple per empty cell."""
    empty_cells = []
    for row in range(9):
        for col in range(9):
            if grid[row][col] == 0:
                possibilities = get_possibilities(grid, row, col)
                empty_cells.append((row, col, possibilities))
    return empty_cells


def update_possibilities(
    empty_cells: list[tuple[int, int, set[int]]], row: int, col: int, number: int
) -> list[tuple[int, int, set[int]]]:
    """Forward checking: a fresh cell list with number dropped from peers of (row, col)."""
    updated_cells = []
    for r, c, possibilities in empty_cells:
        if r == row or c == col or (r // 3 == row // 3 and c // 3 == col // 3):
            new_possibilities = possibilities - {number} if number in possibilities else possibilities
            updated_cells.append((r, c, new_possibilities))
        else:
            updated_cells.append((r, c, possibilities))
    return updated_cells


def solve_backtracking(grid: Grid, empty_cells: list[tuple[int, int, set[int]]]) -> bool:
    """Depth-first backtracking on the MRV cell, propagating each guess onto a fresh list."""
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


def is_valid_sudoku_grid(grid: Grid) -> bool:
    """Check the grid is 9 rows of 9 columns before solving."""
    if len(grid) != 9:
        return False
    for row in grid:
        if len(row) != 9:
            return False
    return True


def solve_sudoku(grid: Grid) -> bool:
    """Collect the empty cells and run the backtracking search on the grid in place."""
    assert is_valid_sudoku_grid(grid), f"Invalid Sudoku grid {grid}"
    empty_cells = get_all_empty_cells_with_possibilities(grid)
    return solve_backtracking(grid, empty_cells)


def solve_one_grid(grid: Grid) -> int:
    """Solve one puzzle in place and read off its top-left 3-digit number."""
    assert solve_sudoku(grid), "failed to solve grid"
    return int("".join(map(str, grid[0][0:3])))


def print_grid(grid_0: Grid, grid_1: Grid) -> None:
    """Pretty-print the unsolved and solved grids side by side (only with --show)."""
    print("     Unsolved Grid       ⟶⟶⟶      Solved Grid        ")
    print("┌───────┬───────┬───────┐   ┌───────┬───────┬───────┐")
    for rb in range(3):
        if rb > 0:
            print("├───────┼───────┼───────┤   ├───────┼───────┼───────┤")
        for r in range(3):
            for cb in range(3):
                print("│", end="")
                for c in range(3):
                    print(" ", end="")
                    print(grid_0[rb * 3 + r][cb * 3 + c] or " ", end="")
                print(" ", end="")
            print("│⟶⟶⟶" if rb == 1 and r == 1 else "│   ", end="")
            for cb in range(3):
                print("│", end="")
                for c in range(3):
                    print(" ", end="")
                    print(grid_1[rb * 3 + r][cb * 3 + c] or " ", end="")
                print(" ", end="")
            print("│ ")
    print("└───────┴───────┴───────┘   └───────┴───────┴───────┘")
    print(" ─────────────────────────────────────────────────── ")


@runner.main
def solve(*args: str) -> str:
    """Backtracking over empty cells with MRV ordering and forward checking; sum the
    top-left 3-digit numbers. Worst case exponential, near-linear on these puzzles."""
    file_url = args[0]

    grids: tuple[Grid, ...] = tuple(get_grids(file_url=file_url))
    s: int = 0
    if runner.show:
        for grid in grids:
            source_grid = copy.deepcopy(grid)
            s += solve_one_grid(grid)
            print_grid(source_grid, grid)
        return str(s)
    return str(sum((solve_one_grid(grid) for grid in grids)))


if __name__ == "__main__":
    raise SystemExit(solve())
