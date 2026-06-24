#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 25: $1000$-digit Fibonacci Number [Level 1]. """
from __future__ import annotations

from solver.runners import runner


@runner.main
def solve(*args: str) -> str:
    """Iterate the Fibonacci recurrence with Python's native big integers until a
    term first reaches n digits (threshold b >= 10**(n-1)); return that term's index.
    O(n^2) digit operations: ~n terms, each addition costing up to O(n) digits."""
    n = runner.parse_int(args[0])

    a, b = (1, 1)
    i = 2
    while b < 10 ** (n - 1):
        a, b = (b, a + b)
        i += 1
    return str(i)


if __name__ == "__main__":
    raise SystemExit(solve())
