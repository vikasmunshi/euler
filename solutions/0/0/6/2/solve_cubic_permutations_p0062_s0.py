#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Migrated from:
  file: euler_solver/solutions/solutions_0001_0100/solution_0062/p0062.py
  func: solve_cubic_permutations_p0062_s0
"""

from __future__ import annotations

from collections import defaultdict
from math import ceil
from sys import argv
from typing import Dict, Set, Tuple


def show_solution() -> bool:
    return "--show" in argv


def n_digit_cubes(digit_length_n: int) -> Tuple[int, ...]:
    start_range: int = ceil((10 ** (digit_length_n - 1)) ** (1 / 3))
    stop_range: int = ceil((10**digit_length_n - 1) ** (1 / 3)) + 1
    return tuple((i**3 for i in range(start_range, stop_range)))


def solve(*, num_permutations: int) -> int:
    digit_length: int = 2
    while True:
        cube_numbers: Tuple[int, ...] = n_digit_cubes(digit_length)
        permuted_cubes: Dict[str, list[int]] = defaultdict(list)
        for cube_number in cube_numbers:
            permuted_cubes["".join(sorted(str(cube_number)))].append(cube_number)
        solutions: Set[int] = set((min(v) for k, v in permuted_cubes.items() if len(v) == num_permutations))
        if solutions:
            if show_solution():
                print(f"Found {len(solutions)} cubes with {num_permutations} permutations of digits: {digit_length}")
                print(f"solutions={solutions!r}")
            return min(solutions)
        digit_length += 1


def main() -> int:
    print(solve(num_permutations=int(argv[1])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
