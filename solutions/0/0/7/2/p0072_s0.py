#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 72: Counting Fractions [Level 4]. """
from __future__ import annotations

from solver.runners import runner


@runner.main
def solve(*args: str) -> str:
    """Sum Euler's totient phi(d) for d in 2..max_d via a multiplicative sieve; O(N log log N).

    The count of reduced proper fractions with denominator exactly d is phi(d), so the answer is
    the running sum of phi(2..max_d). A cell still equal to its index marks a prime, which then
    applies the factor (p-1)/p to every multiple, finalising each totient before its index is read.
    """
    max_d = runner.parse_int(args[0])

    euler_totients: list[int] = list(range(max_d + 1))
    result: int = 0
    for n in range(2, max_d + 1):
        if euler_totients[n] == n:
            for j in range(n, max_d + 1, n):
                euler_totients[j] = euler_totients[j] // n * (n - 1)
        result += euler_totients[n]
    return str(result)


if __name__ == "__main__":
    raise SystemExit(solve())
