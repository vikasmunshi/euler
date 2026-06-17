#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 100: Arranged Probability [Level 6]. """
from __future__ import annotations

from solver.runners import runner


@runner.main
def solve(*args: str) -> str:
    """Solve the Pell equation x^2 - 2*y^2 = -1 by iterating its linear recurrence; O(log total).

    The condition P(BB) = 1/2 rearranges to (2n-1)^2 - 2*(2b-1)^2 = -1, a Pell equation in
    x = 2n-1, y = 2b-1. From the fundamental solution (1, 1) each next solution follows by
    (x, y) -> (3x + 4y, 2x + 3y); x and y stay odd so n and b recover exactly, and solutions
    grow geometrically, so only ~40 steps reach 10^12.
    """
    total_discs = runner.parse_int(args[0])

    x, y = (1, 1)
    while True:
        x, y = (3 * x + 4 * y, 2 * x + 3 * y)
        n = (x + 1) // 2
        b = (y + 1) // 2
        if n >= total_discs:
            return str(b)


if __name__ == "__main__":
    raise SystemExit(solve())
