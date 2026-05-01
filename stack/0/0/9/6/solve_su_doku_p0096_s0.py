#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Migrated from:
  file: euler_solver/solutions/solutions_0001_0100/solution_0096/p0096.py
  func: solve_su_doku_p0096_s0
"""

from __future__ import annotations

from concurrent.futures import Future, as_completed
from concurrent.futures.process import ProcessPoolExecutor
from copy import deepcopy
from pathlib import Path
from sys import argv, setrecursionlimit
from typing import Generator


def show_solution() -> bool:
    return "--show" in argv


def get_text_file(url: str) -> str:
    """Return the contents of a file from the 'resources' directory."""
    local_filename: str = "resources" + "/" + url.split("/")[-1].split("?")[0]
    return (Path(__file__).parent / local_filename).read_text()


Grid = list[list[int]]


def get_grids(file_url: str) -> Generator[Grid, None, None]:
    grid: Grid = []
    for line in get_text_file(url=file_url).splitlines(keepends=False):
        if line.startswith("Grid"):
            grid = []
        else:
            grid.append([int(d) for d in line.strip()])
        if len(grid) == 9:
            yield grid


def print_grid(grid_0: Grid, grid_1: Grid) -> None:
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


def update_possibilities(
    empty_cells: list[tuple[int, int, set[int]]], row: int, col: int, number: int
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


def is_valid_sudoku_grid(grid: Grid) -> bool:
    if len(grid) != 9:
        return False
    for row in grid:
        if len(row) != 9:
            return False
    return True


def solve_sudoku(grid: Grid) -> bool:
    assert is_valid_sudoku_grid(grid), f"Invalid Sudoku grid {grid}"
    empty_cells = get_all_empty_cells_with_possibilities(grid)
    return solve_backtracking(grid, empty_cells)


def solve_one_grid(grid: Grid) -> int:
    assert solve_sudoku(grid), "failed to solve grid"
    return int("".join(map(str, grid[0][0:3])))


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


def main() -> int:
    setrecursionlimit(10**6)
    print(solve(file_url=str(argv[1])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
