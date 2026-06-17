#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 63: Powerful Digit Counts [Level 2]. """
from __future__ import annotations

import math

from solver.runners import runner


def n_digit_nth_powers(n: int) -> tuple[int, ...]:
    """Return every i**n with exactly n digits; bases narrowed by inverting the digit formula."""
    start_range: int = math.ceil((10 ** (n - 1)) ** (1 / n))
    stop_range: int = math.ceil((10**n - 1) ** (1 / n)) + 1
    return tuple((r for i in range(start_range, stop_range) if len(str((r := (i**n)))) == n))


@runner.main
def solve(*args: str) -> str:
    """Count n-digit n-th powers by scanning n upward until no base qualifies; O(1) bounded search.

    Only bases 1..9 can work (base >= 10 gives n+1 digits), and digit count grows sublinearly in n,
    so n is bounded near 21 and the total search is a fixed constant number of candidate pairs.
    """
    result: int = 0
    n: int = 1
    while solutions := n_digit_nth_powers(n):
        result += len(solutions)
        n += 1
        if runner.show:
            print(f"n={n!r} len(solutions)={len(solutions)!r} solutions={solutions!r} ")
    return str(result)


if __name__ == "__main__":
    raise SystemExit(solve())
