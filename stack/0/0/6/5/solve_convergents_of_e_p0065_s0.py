#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Migrated from:
  file: euler_solver/solutions/solutions_0001_0100/solution_0065/p0065.py
  func: solve_convergents_of_e_p0065_s0
"""

from __future__ import annotations

from fractions import Fraction
from sys import argv, setrecursionlimit


def sum_digits(n: int) -> int:
    total: int = 0
    while n:
        total += n % 10
        n //= 10
    return total


def e_denominator(n: int) -> int:
    if n == 1:
        return 2
    elif n % 3 == 0:
        return 2 * n // 3
    else:
        return 1


def nth_convergent_of_e(n: int, *, _n: int = 1) -> Fraction | int:
    if n == _n:
        return e_denominator(_n)
    return e_denominator(_n) + Fraction(1, nth_convergent_of_e(n, _n=_n + 1))


def solve(*, convergent_num: int) -> int:
    return sum_digits(nth_convergent_of_e(convergent_num).numerator)


def main() -> int:
    setrecursionlimit(10**6)
    print(solve(convergent_num=int(argv[1])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
