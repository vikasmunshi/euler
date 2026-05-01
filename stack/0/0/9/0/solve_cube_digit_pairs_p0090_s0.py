#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Migrated from:
  file: euler_solver/solutions/solutions_0001_0100/solution_0090/p0090.py
  func: solve_cube_digit_pairs_p0090_s0
"""

from __future__ import annotations

from itertools import combinations
from typing import List, Tuple


def solve() -> int:
    squares: List[Tuple[int, int]] = [(int((i_sq := f"{i * i:02d}")[0]), int(i_sq[1])) for i in range(1, 10)]

    def can_display(cube_digits: Tuple[int, ...], digit: int) -> bool:
        return digit in cube_digits or (digit in [6, 9] and (6 in cube_digits or 9 in cube_digits))

    def can_pair_display_all(cube1: Tuple[int, ...], cube2: Tuple[int, ...]) -> bool:
        for first_digit, second_digit in squares:
            if not (
                can_display(cube1, first_digit)
                and can_display(cube2, second_digit)
                or (can_display(cube1, second_digit) and can_display(cube2, first_digit))
            ):
                return False
        return True

    all_cubes: List[Tuple[int, ...]] = list(combinations(range(10), 6))
    cube_count: int = len(all_cubes)
    valid_arrangements: int = 0
    for i in range(cube_count):
        for j in range(i, cube_count):
            if can_pair_display_all(all_cubes[i], all_cubes[j]):
                valid_arrangements += 1
    return valid_arrangements


def main() -> int:
    print(solve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
