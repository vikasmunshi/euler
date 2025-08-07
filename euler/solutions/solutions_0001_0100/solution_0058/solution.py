#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
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
    diagonal, but what is more interesting is that 8 out of the 13 numbers
    lying along both diagonals are prime; that is, a ratio of 8 x 13 approximately
    62%.

    If one complete new layer is wrapped around the spiral above, a square
    spiral with side length 9 will be formed. If this process is continued,
    what is the side length of the square spiral for which the ratio of primes
    along both diagonals first falls below 10%?

  Solution Approach:
    To solve this problem, first understand how the spiral's numbers are
    generated and their positions along the diagonals. Each layer added to
    the spiral increases the side length by 2, and the numbers on the diagonals
    of each layer can be expressed through quadratic formulas.

    The key is to generate the numbers on the diagonals layer by layer and
    check which ones are prime. Maintaining a count of total diagonal numbers
    and prime diagonal numbers allows you to compute the ratio of primes along
    the diagonals.

    Efficient primality testing is crucial, as the numbers get large quickly.
    Implement methods like the Miller-Rabin primality test to handle large
    numbers quickly and reliably.

    Iterate this process until the ratio of prime numbers along both diagonals
    falls below 10%, tracking the side length at that point. This approach
    combines number theory for primality checks with careful iteration over
    the spiral's construction.

  Test Cases:
    main:
      threshold=0.1,
      answer=26241.


  Answer: 26241
  URL: https://projecteuler.net/problem=58
"""
from __future__ import annotations

from typing import Generator, Tuple

from euler.logger import logger
from euler.maths import primes
from euler.setup import TestCaseCategory, evaluate, register_solution


def generator_spiral_corners() -> Generator[Tuple[int, int, int, int, int], None, None]:
    layer = 0
    while layer := (layer + 1):
        side_length = 2 * layer + 1
        side_length_min_1 = side_length - 1
        corner_bottom_right = side_length ** 2
        corner_bottom_left = corner_bottom_right - side_length_min_1
        corner_top_left = corner_bottom_left - side_length_min_1
        corner_top_right = corner_top_left - side_length_min_1
        yield (side_length, corner_bottom_right, corner_bottom_left, corner_top_left, corner_top_right)


@register_solution(euler_problem=58, test_case_category=TestCaseCategory.EXTENDED)
def spiral_primes(*, threshold: float) -> int:
    primes.seed_cache()
    num_prime_diagonals: int = 0
    num_diagonal_elements: int = 1
    for side_length, corner_bottom_right, corner_bottom_left, corner_top_left, corner_top_right \
            in generator_spiral_corners():
        num_diagonal_elements += 4
        for corner in (corner_bottom_right, corner_bottom_left, corner_top_left, corner_top_right):
            num_prime_diagonals += primes.is_prime(corner)
        if num_prime_diagonals / num_diagonal_elements < threshold:
            return side_length
    else:
        raise ValueError('No solution found')


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=58, time_out_in_seconds=300, mode='evaluate'))
