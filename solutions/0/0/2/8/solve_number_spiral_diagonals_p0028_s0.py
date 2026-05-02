#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Migrated from:
  file: euler_solver/solutions/solutions_0001_0100/solution_0028/p0028.py
  func: solve_number_spiral_diagonals_p0028_s0
"""

from __future__ import annotations

from sys import argv
from typing import List


def number_spiral_with_diagonal_sum(size: int) -> int:
    x, y, coordinate_map = (0, 0, {(0, 0): 1})
    for number in range(2, size**2 + 1):
        free_adjacent_coords = (c for c in ((x + 1, y), (x, y - 1), (x - 1, y), (x, y + 1)) if c not in coordinate_map)
        x, y = min(((c[0] ** 2 + c[1] ** 2, c) for c in free_adjacent_coords), key=lambda c: c[0])[1]
        coordinate_map[x, y] = number
    msg: List[str] = [f"Generated spiral for size {size} with diagonal elements highlighted in\x1b[34m blue\x1b[0m:"]
    half_size = size // 2
    for row in range(half_size, -half_size - 1, -1):
        row_values = []
        for col in range(-half_size, half_size + 1):
            value = coordinate_map.get((col, row), 0)
            if col == row or col == -row:
                row_values.append(f"\x1b[34m{value:2d}\x1b[0m")
            else:
                row_values.append(f"{value:2d}")
        msg.append(" ".join(row_values))
    diagonal_sum = sum((n for c, n in coordinate_map.items() if c[0] == c[1] or c[0] == -c[1]))
    formula_result = (size * (size * (4 * size + 3) + 8) - 9) // 6
    status = "\x1b[32m✓" if formula_result == diagonal_sum else "\x1b[31m✗"
    msg.append(f"{status} size={size!r}; formula_result={formula_result!r}; diagonal_sum={diagonal_sum!r}\x1b[0m")
    print("\n".join(msg))
    return diagonal_sum


def show_solution() -> bool:
    return "--show" in argv


def solve(*, size: int) -> int:
    if not isinstance(size, int) or size <= 0 or size % 2 == 0:
        raise ValueError("Size must be a positive odd integer")
    if show_solution() and size <= 10:
        return number_spiral_with_diagonal_sum(size)
    return (size * (size * (4 * size + 3) + 8) - 9) // 6


def main() -> int:
    print(solve(size=int(argv[1])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
