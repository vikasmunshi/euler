#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 96: Su Doku [Level 4]. """
from __future__ import annotations

import typing

from solver.runners import runner

Grid = list[list[int]]


def get_grids(file_url: str) -> typing.Generator[Grid, None, None]:
    """Yield each 9x9 puzzle from the resource file, skipping the 'Grid NN' labels."""
    grid: Grid = []
    for line in runner.get_text_file(file_url).splitlines(keepends=False):
        if line.startswith('Grid'):
            grid = []
        else:
            grid.append([int(d) for d in line.strip()])
        if len(grid) == 9:
            yield grid


class DancingLinks:
    """Knuth's Algorithm X over a toroidal doubly-linked node mesh (Dancing Links).

    Sudoku is encoded as an exact-cover instance with 324 columns (constraints) -
    81 cell, 81 row-digit, 81 column-digit, 81 box-digit - and one matrix row per
    legal (row, col, digit) placement, each covering exactly those 4 columns.
    """

    # Node fields are parallel arrays indexed by node id, the natural shape for the
    # pointer surgery of cover/uncover (and a faithful match for the C port).
    def __init__(self, num_columns: int, max_nodes: int) -> None:
        """Allocate the node arrays and link the header ring of num_columns columns."""
        self.left: list[int] = [0] * max_nodes
        self.right: list[int] = [0] * max_nodes
        self.up: list[int] = [0] * max_nodes
        self.down: list[int] = [0] * max_nodes
        self.column: list[int] = [0] * max_nodes  # column header of each node
        self.size: list[int] = [0] * max_nodes    # live node count per column header
        self.row_id: list[int] = [0] * max_nodes  # encodes (row, col, digit) of a node
        # Headers occupy ids 0..num_columns; id 0 is the root, 1..num_columns columns.
        for c in range(num_columns + 1):
            self.left[c] = c - 1
            self.right[c] = c + 1
            self.up[c] = c
            self.down[c] = c
            self.column[c] = c
        self.left[0] = num_columns
        self.right[num_columns] = 0
        self.node_count: int = num_columns + 1

    def add_row(self, row_id: int, columns: tuple[int, int, int, int]) -> None:
        """Splice one matrix row (4 nodes) into its column lists, linked in a ring."""
        first: int = -1
        prev: int = -1
        for col in columns:
            node: int = self.node_count
            self.node_count += 1
            self.row_id[node] = row_id
            self.column[node] = col
            # Insert above the header (i.e. at the bottom of the column ring).
            self.down[node] = col
            self.up[node] = self.up[col]
            self.down[self.up[col]] = node
            self.up[col] = node
            self.size[col] += 1
            if first == -1:
                first = node
                self.left[node] = node
                self.right[node] = node
            else:
                self.right[node] = first
                self.left[node] = prev
                self.right[prev] = node
                self.left[first] = node
            prev = node

    def cover(self, col: int) -> None:
        """Remove a column header and every row that intersects it from the mesh."""
        self.right[self.left[col]] = self.right[col]
        self.left[self.right[col]] = self.left[col]
        i: int = self.down[col]
        while i != col:
            j: int = self.right[i]
            while j != i:
                self.down[self.up[j]] = self.down[j]
                self.up[self.down[j]] = self.up[j]
                self.size[self.column[j]] -= 1
                j = self.right[j]
            i = self.down[i]

    def uncover(self, col: int) -> None:
        """Re-insert a column and its rows, exactly reversing cover()."""
        i: int = self.up[col]
        while i != col:
            j: int = self.left[i]
            while j != i:
                self.size[self.column[j]] += 1
                self.down[self.up[j]] = j
                self.up[self.down[j]] = j
                j = self.left[j]
            i = self.up[i]
        self.right[self.left[col]] = col
        self.left[self.right[col]] = col

    def search(self, solution: list[int]) -> bool:
        """Recurse, always covering the column with fewest options (the S heuristic)."""
        if self.right[0] == 0:
            return True
        col: int = self.right[0]
        best: int = self.size[col]
        c: int = self.right[0]
        while c != 0:
            if self.size[c] < best:
                best = self.size[c]
                col = c
            c = self.right[c]
        self.cover(col)
        r: int = self.down[col]
        while r != col:
            solution.append(r)
            j: int = self.right[r]
            while j != r:
                self.cover(self.column[j])
                j = self.right[j]
            if self.search(solution):
                return True
            solution.pop()
            j = self.left[r]
            while j != r:
                self.uncover(self.column[j])
                j = self.left[j]
            r = self.down[r]
        self.uncover(col)
        return False


def solve_one_grid(grid: Grid) -> int:
    """Build the exact-cover matrix, solve it, and read off the top-left 3-digit number."""
    # 324 constraint columns; at most 9*81 placement rows, 4 nodes each, plus headers.
    dlx = DancingLinks(324, 325 + 9 * 81 * 4)
    for row in range(9):
        for col in range(9):
            clue: int = grid[row][col]
            box: int = (row // 3) * 3 + col // 3
            for digit in (range(1, 10) if clue == 0 else (clue,)):
                # Column ids are 1-based; the four covered constraints for (row,col,digit).
                cols: tuple[int, int, int, int] = (
                    1 + row * 9 + col,
                    1 + 81 + row * 9 + (digit - 1),
                    1 + 162 + col * 9 + (digit - 1),
                    1 + 243 + box * 9 + (digit - 1),
                )
                dlx.add_row((row * 9 + col) * 9 + (digit - 1), cols)
    solution: list[int] = []
    assert dlx.search(solution), 'failed to solve grid'
    for node in solution:
        rid: int = dlx.row_id[node]
        r, c, d = rid // 81, (rid // 9) % 9, rid % 9 + 1
        grid[r][c] = d
    return int(''.join(str(grid[0][c]) for c in range(3)))


@runner.main
def solve(*args: str) -> str:
    """Reduce each grid to exact cover and solve with Algorithm X / Dancing Links; sum the
    top-left 3-digit numbers. Worst case exponential, near-linear on these puzzles."""
    file_url = args[0]

    return str(sum(solve_one_grid(grid) for grid in get_grids(file_url=file_url)))


if __name__ == "__main__":
    raise SystemExit(solve())
