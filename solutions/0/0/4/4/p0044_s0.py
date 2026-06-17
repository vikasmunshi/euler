#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 44: Pentagon Numbers [Level 2]. """
from __future__ import annotations

import math

from solver.runners import runner


def nth_pentagonal_number(n: int) -> int:
    """Return the n-th pentagonal number via the closed form n(3n-1)/2."""
    return n * (3 * n - 1) // 2


def is_pentagonal_number(n: int) -> bool:
    """Test pentagonality in O(1) by inverting the quadratic: n = (1 + sqrt(1 + 24m)) / 6."""
    return ((1 + math.sqrt(1 + 24 * n)) / 6).is_integer()


@runner.main
def solve(*args: str) -> str:
    """Scan outer index i upward and inner index j downward, returning the first pair whose
    sum and difference are both pentagonal; the descending inner loop makes that first hit the
    minimal difference for each i, and the ascending outer loop makes it the global minimum.
    O(i_answer^2) constant-time pentagonality tests."""
    i = 0
    while i := (i + 1):
        p_i = nth_pentagonal_number(i)
        for j in range(i - 1, 0, -1):
            p_j = nth_pentagonal_number(j)
            if is_pentagonal_number(p_i - p_j) and is_pentagonal_number(p_i + p_j):
                return str(p_i - p_j)
    else:
        raise ValueError("No solution found")


if __name__ == "__main__":
    raise SystemExit(solve())
