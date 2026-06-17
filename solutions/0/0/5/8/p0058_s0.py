#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 58: Spiral Primes [Level 2]. """
from __future__ import annotations

import typing

from solver.runners import runner


def generator_spiral_corners() -> typing.Generator[tuple[int, int, int, int, int], None, None]:
    """Yield (side_length, four corners) for each layer; corners are arithmetic from (2k+1)^2."""
    layer = 0
    while layer := (layer + 1):
        side_length = 2 * layer + 1
        side_length_min_1 = side_length - 1
        bottom_right = side_length**2
        bottom_left = bottom_right - side_length_min_1
        top_left = bottom_left - side_length_min_1
        top_right = top_left - side_length_min_1
        yield (side_length, bottom_right, bottom_left, top_left, top_right)


def is_prime(num: int) -> bool:
    """Trial division by odd divisors up to sqrt(num); O(sqrt(num))."""
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


@runner.main
def solve(*args: str) -> str:
    """Scan spiral layers, counting prime diagonal corners until the running ratio drops below
    the threshold; O(n^2) in the side length n, dominated by per-corner trial division."""
    threshold = float(args[0])

    num_prime_diagonals: int = 0
    num_diagonal_elements: int = 1
    for side_length, bottom_right, bottom_left, top_left, top_right in generator_spiral_corners():
        num_diagonal_elements += 4
        for corner in (bottom_right, bottom_left, top_left, top_right):
            num_prime_diagonals += is_prime(corner)
        if num_prime_diagonals / num_diagonal_elements < threshold:
            return str(side_length)
    else:
        raise ValueError("No solution found")


if __name__ == "__main__":
    raise SystemExit(solve())
