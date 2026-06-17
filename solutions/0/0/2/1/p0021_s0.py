#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 21: Amicable Numbers [Level 1]. """
from __future__ import annotations

import functools

from solver.runners import runner


@runner.main
def solve(*args: str) -> str:
    """Sum every amicable number in [2, max_num].

    For each x let y = d(x), the sum of proper divisors; x is amicable when
    y != x and d(y) == x. d(n) is computed by O(sqrt(n)) divisor pairing and
    memoised per call, giving an overall O(max_num * sqrt(max_num)) cost. The
    cache is built inside solve() so each benchmark run pays its full cost.
    """
    max_num = runner.parse_int(args[0])

    @functools.lru_cache(maxsize=None)
    def sum_factors(n: int) -> int:
        """Sum of the proper divisors of n, via square-root divisor pairing."""
        n_sqrt = int(n**0.5)
        return 1 + sum((i + n // i for i in range(2, n_sqrt + 1) if n % i == 0)) - (n_sqrt if n_sqrt**2 == n else 0)

    return str(sum((x for x in range(2, max_num + 1) if (y := sum_factors(x)) != x and sum_factors(y) == x)))


if __name__ == "__main__":
    raise SystemExit(solve())
