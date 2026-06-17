#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 86: Cuboid Route [Level 6]. """
from __future__ import annotations

import itertools
import math

from solver.runners import runner


@runner.main
def solve(*args: str) -> str:
    """Unfold the cuboid: shortest surface path is sqrt(a^2 + (b+c)^2) under a >= b >= c.

    Fix the largest dimension a, scan s = b+c, test a^2 + s^2 for a perfect square once per
    s, and add the O(1) count of (b, c) pairs (with b <= a) summing to s; accumulate
    monotonically and return at the threshold. O(M^2) in the answer M.
    """
    target_solutions = runner.parse_int(args[0])

    result: int = 0
    for a in itertools.count(1):
        for b_plus_c in range(1, 2 * a + 1):
            if math.sqrt(a**2 + b_plus_c**2).is_integer():
                # b+c <= a+1: cap b <= a is slack, floor(s/2) pairs; else the cap binds.
                result += b_plus_c // 2 if b_plus_c <= a + 1 else (2 * a - b_plus_c + 2) // 2
                if result >= target_solutions:
                    return str(a)
    return str(-1)


if __name__ == "__main__":
    raise SystemExit(solve())
