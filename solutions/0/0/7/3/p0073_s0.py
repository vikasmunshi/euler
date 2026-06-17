#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 73: Counting Fractions in a Range [Level 3]. """
from __future__ import annotations

from solver.runners import runner


@runner.main
def solve(*args: str) -> str:
    """Iterative Farey neighbour traversal of (1/3, 1/2): the neighbour identity bc - ad = 1 gives
    the next denominator as max_d - ((max_d + prev_d) % d). Only denominators are tracked since the
    boundaries fix every numerator. O(answer)."""
    max_d = runner.parse_int(args[0])

    lower_denominator: int = 3
    upper_denominator: int = 2
    # Largest denominator of the form 2 + 3k not exceeding max_d: the fraction just above 1/3.
    d = upper_denominator + lower_denominator * ((max_d - upper_denominator) // lower_denominator)
    prev_d = lower_denominator
    count = 0
    # Walk upward, counting one fraction per step; stop at denominator 2 (the upper bound 1/2).
    while d != upper_denominator:
        count += 1
        prev_d, d = (d, max_d - (max_d + prev_d) % d)
    return str(count)


if __name__ == "__main__":
    raise SystemExit(solve())
