#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Sudoku Solver """
from __future__ import annotations

from typing import Generator

Grid = list[list[int]]


def is_valid_sudoku_grid(grid: Grid) -> bool:
    if len(grid) != 9:
        return False
    for row in grid:
        if len(row) != 9:
            return False
    return True


def solve_sudoku(grid: Grid) -> bool:
    assert is_valid_sudoku_grid(grid), f'Invalid Sudoku grid {grid}'
    empty_cells = get_all_empty_cells_with_possibilities(grid)
    return solve_backtracking(grid, empty_cells)


def solve_backtracking(grid: Grid, empty_cells: list[tuple[int, int, set[int]]]) -> bool:
    if not empty_cells:
        return True  # All cells are filled

    # Sort or select the cell with the fewest possibilities (MRV heuristic)
    empty_cells.sort(key=lambda c: len(c[2]))
    row, col, possibilities = empty_cells.pop(0)

    for possibility in possibilities:
        grid[row][col] = possibility
        updated_cells = update_possibilities(empty_cells, row, col, possibility)
        if solve_backtracking(grid, updated_cells):  # Recurse
            return True
        grid[row][col] = 0  # Backtrack

    empty_cells.insert(0, (row, col, possibilities))
    return False


def get_all_empty_cells_with_possibilities(grid: Grid) -> list[tuple[int, int, set[int]]]:
    empty_cells = []
    for row in range(9):
        for col in range(9):
            if grid[row][col] == 0:
                possibilities = get_possibilities(grid, row, col)
                empty_cells.append((row, col, possibilities))
    return empty_cells


def update_possibilities(empty_cells: list[tuple[int, int, set[int]]],
                         row: int, col: int, number: int) -> list[tuple[int, int, set[int]]]:
    updated_cells = []
    for r, c, possibilities in empty_cells:
        if r == row or c == col or (r // 3 == row // 3 and c // 3 == col // 3):
            new_possibilities = possibilities - {number} if number in possibilities else possibilities
            updated_cells.append((r, c, new_possibilities))
        else:
            updated_cells.append((r, c, possibilities))
    return updated_cells


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


"""
 ───────────────────────────────────────────────────
     Unsolved Grid       ⟶⟶⟶      Solved Grid
┌───────┬───────┬───────┐   ┌───────┬───────┬───────┐
│ 3     │ 2     │       │   │ 3 5 1 │ 2 8 6 │ 4 9 7 │
│       │ 1   7 │       │   │ 4 9 2 │ 1 5 7 │ 6 3 8 │
│ 7   6 │   3   │ 5     │   │ 7 8 6 │ 9 3 4 │ 5 1 2 │
├───────┼───────┼───────┤   ├───────┼───────┼───────┤
│   7   │     9 │   8   │   │ 2 7 5 │ 4 6 9 │ 1 8 3 │
│ 9     │   2   │     4 │⟶⟶⟶│ 9 3 8 │ 5 2 1 │ 7 6 4 │
│   1   │ 8     │   5   │   │ 6 1 4 │ 8 7 3 │ 2 5 9 │
├───────┼───────┼───────┤   ├───────┼───────┼───────┤
│     9 │   4   │ 3   1 │   │ 8 2 9 │ 6 4 5 │ 3 7 1 │
│       │ 7   2 │       │   │ 1 6 3 │ 7 9 2 │ 8 4 5 │
│       │     8 │     6 │   │ 5 4 7 │ 3 1 8 │ 9 2 6 │
└───────┴───────┴───────┘   └───────┴───────┴───────┘
 ───────────────────────────────────────────────────
"""
