#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Migrated from:
  file: euler_solver/solutions/solutions_0001_0100/solution_0058/p0058.py
  func: solve_spiral_primes_p0058_s0
"""

from __future__ import annotations

from sys import argv
from typing import Generator, Tuple


def is_prime(num: int) -> bool:
    if num < 2:
        return False
    if num == 2:
        return True
    if num % 2 == 0:
        return False
    i = 3
    while i * i <= num:
        if num % i == 0:
            return False
        i += 2
    return True


def generator_spiral_corners() -> Generator[Tuple[int, int, int, int, int], None, None]:
    layer = 0
    while layer := (layer + 1):
        side_length = 2 * layer + 1
        side_length_min_1 = side_length - 1
        bottom_right = side_length**2
        bottom_left = bottom_right - side_length_min_1
        top_left = bottom_left - side_length_min_1
        top_right = top_left - side_length_min_1
        yield (side_length, bottom_right, bottom_left, top_left, top_right)


def solve(*, threshold: float) -> int:
    num_prime_diagonals: int = 0
    num_diagonal_elements: int = 1
    for side_length, bottom_right, bottom_left, top_left, top_right in generator_spiral_corners():
        num_diagonal_elements += 4
        for corner in (bottom_right, bottom_left, top_left, top_right):
            num_prime_diagonals += is_prime(corner)
        if num_prime_diagonals / num_diagonal_elements < threshold:
            return side_length
    else:
        raise ValueError("No solution found")


def main() -> int:
    print(solve(threshold=float(argv[1])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
