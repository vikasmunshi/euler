#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 1: Multiples of 3 or 5 [Level 0]. """
from __future__ import annotations

from solver.runners import runner


def sum_arithmetic_series(common_difference: int, *, max_limit: int) -> int:
    """Closed-form sum of 0, d, 2d, ... below max_limit: d*n(n+1)/2."""
    n = (max_limit - 1) // common_difference
    return common_difference * (n * (n + 1)) // 2


@runner.main
def solve(*args: str) -> str:
    """Multiples of 3 or 5 below the limit by inclusion-exclusion (3 + 5 - 15),
    each part from the closed-form arithmetic series. O(1)."""
    max_limit: int = runner.parse_int(args[0])
    return str(
        sum_arithmetic_series(3, max_limit=max_limit)
        + sum_arithmetic_series(5, max_limit=max_limit)
        - sum_arithmetic_series(15, max_limit=max_limit)
    )


if __name__ == "__main__":
    raise SystemExit(solve())
