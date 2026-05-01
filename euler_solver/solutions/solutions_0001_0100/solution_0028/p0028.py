#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 28: Number Spiral Diagonals.

Problem Statement:
    Starting with the number 1 and moving to the right in a clockwise direction a 5 by 5
    spiral is formed as follows:

    21 22 23 24 25
    20  7  8  9 10
    19  6  1  2 11
    18  5  4  3 12
    17 16 15 14 13

    It can be verified that the sum of the numbers on the diagonals is 101.

    What is the sum of the numbers on the diagonals in a 1001 by 1001 spiral formed in
    the same way?

Solution Approach:
    Use a mathematical pattern observation of the spiral corners to formulate a sum
    of diagonal elements directly without building the entire spiral matrix.
    Key idea: number theory and arithmetic series summation. Complexity O(1).

Answer: 669171001
URL: https://projecteuler.net/problem=28
"""
from __future__ import annotations

from typing import Any, List

from euler_solver.framework import evaluate, logger, register_solution, show_solution

euler_problem: int = 28
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'size': 5}, 'answer': 101},
    {'category': 'dev', 'input': {'size': 7}, 'answer': 261},
    {'category': 'dev', 'input': {'size': 9}, 'answer': 537},
    {'category': 'main', 'input': {'size': 1001}, 'answer': 669171001},
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_number_spiral_diagonals_p0028_s0(*, size: int) -> int:
    if not isinstance(size, int) or size <= 0 or size % 2 == 0:
        raise ValueError('Size must be a positive odd integer')
    if show_solution() and size <= 10:
        return number_spiral_with_diagonal_sum(size)
    return (size * (size * (4 * size + 3) + 8) - 9) // 6


def number_spiral_with_diagonal_sum(size: int) -> int:
    x, y, coordinate_map = (0, 0, {(0, 0): 1})
    for number in range(2, size ** 2 + 1):
        free_adjacent_coords = (c for c in ((x + 1, y), (x, y - 1), (x - 1, y), (x, y + 1)) if c not in coordinate_map)
        x, y = min(((c[0] ** 2 + c[1] ** 2, c) for c in free_adjacent_coords), key=lambda c: c[0])[1]
        coordinate_map[x, y] = number
    msg: List[str] = [f'Generated spiral for size {size} with diagonal elements highlighted in\x1b[34m blue\x1b[0m:']
    half_size = size // 2
    for row in range(half_size, -half_size - 1, -1):
        row_values = []
        for col in range(-half_size, half_size + 1):
            value = coordinate_map.get((col, row), 0)
            if col == row or col == -row:
                row_values.append(f'\x1b[34m{value:2d}\x1b[0m')
            else:
                row_values.append(f'{value:2d}')
        msg.append(' '.join(row_values))
    diagonal_sum = sum((n for c, n in coordinate_map.items() if c[0] == c[1] or c[0] == -c[1]))
    formula_result = (size * (size * (4 * size + 3) + 8) - 9) // 6
    status = '\x1b[32m✓' if formula_result == diagonal_sum else '\x1b[31m✗'
    msg.append(f'{status} size={size!r}; formula_result={formula_result!r}; diagonal_sum={diagonal_sum!r}\x1b[0m')
    print('\n'.join(msg))
    return diagonal_sum


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
