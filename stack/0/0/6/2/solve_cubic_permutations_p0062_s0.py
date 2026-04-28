#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Migrated from
    euler_solver/solutions/solutions_0001_0100/solution_0062/p0062.py :: solve_cubic_permutations_p0062_s0.

Project Euler Problem 62: Cubic Permutations.

Problem Statement:
    The cube, 41063625 (345^3), can be permuted to produce two other cubes:
    56623104 (384^3) and 66430125 (405^3). In fact, 41063625 is the smallest cube
    which has exactly three permutations of its digits which are also cube.

    Find the smallest cube for which exactly five permutations of its digits are cube.

Solution Approach:
    Use digit manipulation and hashing. Generate cubes and group by sorted digit
    signatures. Use a dictionary to count permutations that are cubes. Stop when a
    group reaches exactly five permutations. Time complexity roughly O(N) where N
    depends on iteration limit; space depends on hash storage.

Answer: 127035954683
URL: https://projecteuler.net/problem=62"""
from __future__ import annotations

import sys
from collections import defaultdict
from math import ceil
from typing import Dict, Set, Tuple


def show_solution() -> bool:
    return '--show' in sys.argv


def n_digit_cubes(digit_length_n: int) -> Tuple[int, ...]:
    start_range: int = ceil((10 ** (digit_length_n - 1)) ** (1 / 3))
    stop_range: int = ceil((10 ** digit_length_n - 1) ** (1 / 3)) + 1
    return tuple((i ** 3 for i in range(start_range, stop_range)))


def solve(*, num_permutations: int) -> int:
    digit_length: int = 2
    while True:
        cube_numbers: Tuple[int, ...] = n_digit_cubes(digit_length)
        permuted_cubes: Dict[str, list[int]] = defaultdict(list)
        for cube_number in cube_numbers:
            permuted_cubes[''.join(sorted(str(cube_number)))].append(cube_number)
        solutions: Set[int] = set((min(v) for k, v in permuted_cubes.items() if len(v) == num_permutations))
        if solutions:
            if show_solution():
                print(f'Found {len(solutions)} cubes with {num_permutations} permutations of digits: {digit_length}',
                      file=sys.stderr, )
                print(f'solutions={solutions!r}', file=sys.stderr)
            return min(solutions)
        digit_length += 1


if __name__ == '__main__':
    print(solve(num_permutations=int(sys.argv[1])))
