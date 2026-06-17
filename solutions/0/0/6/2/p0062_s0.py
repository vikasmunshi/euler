#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 62: Cubic Permutations [Level 2]. """
from __future__ import annotations

import collections
import math

from solver.runners import runner


def n_digit_cubes(digit_length_n: int) -> tuple[int, ...]:
    """Return all cubes with exactly digit_length_n digits, via ceil(cbrt(.)) bounds on the cube root."""
    start_range: int = math.ceil((10 ** (digit_length_n - 1)) ** (1 / 3))
    stop_range: int = math.ceil((10**digit_length_n - 1) ** (1 / 3)) + 1
    return tuple((i**3 for i in range(start_range, stop_range)))


@runner.main
def solve(*args: str) -> str:
    """Group cubes by digit-length band, keyed by sorted-digit string (canonical for permutations);
    the first band with a group of exactly num_permutations cubes gives the smallest answer.
    O(10^(d/3) * d log d) up to the answer's digit-length d."""
    num_permutations = runner.parse_int(args[0])

    digit_length: int = 2
    while True:
        cube_numbers: tuple[int, ...] = n_digit_cubes(digit_length)
        permuted_cubes: dict[str, list[int]] = collections.defaultdict(list)
        for cube_number in cube_numbers:
            permuted_cubes["".join(sorted(str(cube_number)))].append(cube_number)
        solutions: set[int] = set((min(v) for k, v in permuted_cubes.items() if len(v) == num_permutations))
        if solutions:
            if runner.show:
                print(f"Found {len(solutions)} cubes with {num_permutations} permutations of digits: {digit_length}")
                print(f"solutions={solutions!r}")
            return str(min(solutions))
        digit_length += 1


if __name__ == "__main__":
    raise SystemExit(solve())
