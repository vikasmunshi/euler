#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 65: Convergents of $e$ [Level 2]. """
from __future__ import annotations

import fractions
import sys

from solver.runners import runner


def e_denominator(n: int) -> int:
    """Return the n-th partial quotient of e: 2 at n==1, 2*(n/3) when 3 | n, else 1."""
    if n == 1:
        return 2
    elif n % 3 == 0:
        return 2 * n // 3
    else:
        return 1


def nth_convergent_of_e(n: int, *, _n: int = 1) -> fractions.Fraction | int:
    """Evaluate the n-th convergent exactly by recursing to depth n and unwinding a + 1/rest."""
    if n == _n:
        return e_denominator(_n)
    return e_denominator(_n) + fractions.Fraction(1, nth_convergent_of_e(n, _n=_n + 1))


def sum_digits(n: int) -> int:
    """Sum the decimal digits of n via repeated mod-10 division."""
    total: int = 0
    while n:
        total += n % 10
        n //= 10
    return total


@runner.main
def solve(*args: str) -> str:
    """Build the n-th convergent of e with exact Fraction arithmetic, then sum its numerator's
    digits; recursion depth and rational sizes both grow with n, so cost is ~O(n^2) digit-ops."""
    convergent_num = runner.parse_int(args[0])
    sys.setrecursionlimit(10 ** 6)

    return str(sum_digits(nth_convergent_of_e(convergent_num).numerator))


if __name__ == "__main__":
    raise SystemExit(solve())
