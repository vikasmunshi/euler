#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 90: Cube Digit Pairs [Level 9]. """
from __future__ import annotations

import itertools

from solver.runners import runner


@runner.main
def solve(*args: str) -> str:
    """Brute-force over all unordered pairs of the C(10,6)=210 six-digit cubes; O(210^2 * 9)."""
    squares: list[tuple[int, int]] = [(int((i_sq := f"{i * i:02d}")[0]), int(i_sq[1])) for i in range(1, 10)]

    def can_display(cube_digits: tuple[int, ...], digit: int) -> bool:
        """True if the cube shows the digit, treating 6 and 9 as interchangeable via the flip rule."""
        return digit in cube_digits or (digit in [6, 9] and (6 in cube_digits or 9 in cube_digits))

    def can_pair_display_all(cube1: tuple[int, ...], cube2: tuple[int, ...]) -> bool:
        """True if every square's two digits can be shown, with either cube supplying the tens digit."""
        for first_digit, second_digit in squares:
            if not (
                can_display(cube1, first_digit)
                and can_display(cube2, second_digit)
                or (can_display(cube1, second_digit) and can_display(cube2, first_digit))
            ):
                return False
        return True

    all_cubes: list[tuple[int, ...]] = list(itertools.combinations(range(10), 6))
    cube_count: int = len(all_cubes)
    valid_arrangements: int = 0
    # Triangular iteration (j from i) counts each unordered pair once and admits self-pairs.
    for i in range(cube_count):
        for j in range(i, cube_count):
            if can_pair_display_all(all_cubes[i], all_cubes[j]):
                valid_arrangements += 1
    return str(valid_arrangements)


if __name__ == "__main__":
    raise SystemExit(solve())
