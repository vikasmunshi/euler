#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 58: Spiral Primes.

Problem Statement:
    Starting with 1 and spiralling anticlockwise in the following way, a square
    spiral with side length 7 is formed.

        37 36 35 34 33 32 31
        38 17 16 15 14 13 30
        39 18  5  4  3 12 29
        40 19  6  1  2 11 28
        41 20  7  8  9 10 27
        42 21 22 23 24 25 26
        43 44 45 46 47 48 49

    It is interesting to note that the odd squares lie along the bottom right
    diagonal, but what is more interesting is that 8 out of the 13 numbers lying
    along both diagonals are prime; that is, a ratio of 8/13 approximately 62%.

    If one complete new layer is wrapped around the spiral above, a square spiral
    with side length 9 will be formed. If this process is continued, what is the
    side length of the square spiral for which the ratio of primes along both
    diagonals first falls below 10%?

Solution Approach:
    Use number theory and prime checking efficiently for the diagonals of each
    spiral layer. The diagonals for layer k (side length 2k+1) are computed arithmetically.
    Maintain running counts of prime numbers vs total diagonal numbers to find
    when ratio drops below 10%. Employ a fast primality test for large numbers.
    Expected time complexity depends on primality testing but should be efficient
    with optimizations.

Answer: 26241
URL: https://projecteuler.net/problem=58
"""
from __future__ import annotations

from typing import Any, Generator, Tuple

from euler_solver.framework import evaluate, logger, register_solution
from euler_solver.lib_primes import is_prime

euler_problem: int = 58
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'threshold': 0.1}, 'answer': 26241},
]


def generator_spiral_corners() -> Generator[Tuple[int, int, int, int, int], None, None]:
    layer = 0
    while layer := (layer + 1):
        side_length = 2 * layer + 1
        side_length_min_1 = side_length - 1
        bottom_right = side_length ** 2
        bottom_left = bottom_right - side_length_min_1
        top_left = bottom_left - side_length_min_1
        top_right = top_left - side_length_min_1
        yield side_length, bottom_right, bottom_left, top_left, top_right


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_spiral_primes_p0058_s0(*, threshold: float) -> int:
    num_prime_diagonals: int = 0
    num_diagonal_elements: int = 1
    for side_length, bottom_right, bottom_left, top_left, top_right in generator_spiral_corners():
        num_diagonal_elements += 4
        for corner in (bottom_right, bottom_left, top_left, top_right):
            num_prime_diagonals += is_prime(corner)
        if num_prime_diagonals / num_diagonal_elements < threshold:
            return side_length
    else:
        raise ValueError('No solution found')


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
