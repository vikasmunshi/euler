#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
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
URL: https://projecteuler.net/problem=62
"""
from __future__ import annotations

from collections import defaultdict
from math import ceil
from typing import Any, Dict, Set, Tuple

from euler_solver.framework import evaluate, logger, register_solution, show_solution

euler_problem: int = 62
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'num_permutations': 2}, 'answer': 125},
    {'category': 'dev', 'input': {'num_permutations': 3}, 'answer': 41063625},
    {'category': 'dev', 'input': {'num_permutations': 4}, 'answer': 1006012008},
    {'category': 'main', 'input': {'num_permutations': 5}, 'answer': 127035954683},
    {'category': 'extra', 'input': {'num_permutations': 6}, 'answer': 1000600120008},
    {'category': 'extra', 'input': {'num_permutations': 7}, 'answer': 10569784298536},
    {'category': 'extra', 'input': {'num_permutations': 8}, 'answer': 10314675896832},
    {'category': 'extra', 'input': {'num_permutations': 9}, 'answer': 13465983902671},
]


def n_digit_cubes(digit_length_n: int) -> Tuple[int, ...]:
    start_range: int = ceil((10 ** (digit_length_n - 1)) ** (1 / 3))
    stop_range: int = ceil((10 ** digit_length_n - 1) ** (1 / 3)) + 1
    return tuple((i ** 3 for i in range(start_range, stop_range)))


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_cubic_permutations_p0062_s0(*, num_permutations: int) -> int:
    digit_length: int = 2
    while True:
        cube_numbers: Tuple[int, ...] = n_digit_cubes(digit_length)
        permuted_cubes: Dict[str, list[int]] = defaultdict(list)
        for cube_number in cube_numbers:
            permuted_cubes[''.join(sorted(str(cube_number)))].append(cube_number)
        solutions: Set[int] = set((min(v) for k, v in permuted_cubes.items() if len(v) == num_permutations))
        if solutions:
            if show_solution():
                print(f'Found {len(solutions)} cubes with {num_permutations} permutations of digits: {digit_length}')
                print(f'solutions={solutions!r}')
            return min(solutions)
        digit_length += 1


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
