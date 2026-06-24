#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 7: 10 001st Prime [Level 0]. """
from __future__ import annotations

import math

from solver.runners import runner


@runner.main
def solve(*args: str) -> str:
    """Sieve of Sundaram over [1, n·ln n] (the prime-number-theorem bound on the n-th prime):
    each surviving index k denotes the odd prime 2k+1, so the (n-2)-th survivor (after the
    special-cased prime 2) is the n-th prime. O(M log M) marking for M = n·ln n."""
    n = runner.parse_int(args[0])

    if n == 1:
        return str(2)
    max_expected_value = int(n * math.log(n))
    numbers = list(range(0, max_expected_value + 1))
    for i in numbers[1:]:
        for j in range(i, max_expected_value + 1):
            try:
                numbers[i + j + 2 * i * j] = 0
            except IndexError:
                break
    return str(2 * [i for i in numbers if i != 0][n - 2] + 1)


if __name__ == "__main__":
    raise SystemExit(solve())
