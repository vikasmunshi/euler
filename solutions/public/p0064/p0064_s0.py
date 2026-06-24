#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 64: Odd Period Square Roots [Level 3]. """
from __future__ import annotations

import math

from solver.runners import runner


def get_period_length(n: int) -> int:
    """Period of the continued fraction of sqrt(n) via cycle detection on the integer
    state triple (m, d, a) of the quadratic-irrational recurrence; O(period) per call."""
    a0 = a = math.isqrt(n)
    d, m, p = (1, 0, [])
    while True:
        m = d * a - m
        d = (n - m**2) // d
        a = (a0 + m) // d
        if (m, d, a) in p:
            break
        p.append((m, d, a))
    return len(p)


@runner.main
def solve(*args: str) -> str:
    """Count non-square N <= limit whose sqrt(N) continued fraction has odd period;
    sums an odd-period predicate over a generator; O(limit * sqrt(limit))."""
    max_limit = runner.parse_int(args[0])

    return str(sum((get_period_length(n) % 2 == 1 for n in range(2, max_limit + 1) if not math.sqrt(n).is_integer())))


if __name__ == "__main__":
    raise SystemExit(solve())
