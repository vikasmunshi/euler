#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 94: Almost Equilateral Triangles [Level 14]. """
from __future__ import annotations

from solver.runners import runner


@runner.main
def solve(*args: str) -> str:
    """Generate valid perimeters via the Pell recurrence x^2 - 3 y^2 = 1; O(log N).

    The integral-area condition reduces to a Pell-type equation whose solutions follow a
    linear recurrence; both triangle families (third side a+1 and a-1) are interleaved
    into one increasing sequence using the sign alternator m, so terms grow ~4x per step.
    """
    max_perimeter = runner.parse_int(args[0])

    s, s1, s2, m, p = (0, 1, 1, 1, 0)
    while p <= max_perimeter:
        # Parallel assignment evaluates all old values first: new s2 uses old s1/s2, new m flips.
        s, s1, s2, m = (s + p, s2, 4 * s2 - s1 + 2 * m, -m)
        p = 3 * s2 - m
    return str(s)


if __name__ == "__main__":
    raise SystemExit(solve())
