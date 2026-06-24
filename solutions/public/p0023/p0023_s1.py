#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 23: Non-Abundant Sums [Level 2]. """
from __future__ import annotations

from solver.runners import runner


def sum_proper_divisors(n: int) -> int:
    """Sum of the proper divisors of n, by trial division up to sqrt(n)."""
    if n <= 1:
        return 0
    result = 1
    i = 2
    while i * i <= n:
        if n % i == 0:
            result += i
            if i != n // i:
                result += n // i
        i += 1
    return result


@runner.main
def solve(*args: str) -> str:
    """Classify abundant numbers via trial-division divisor sums, mark every pairwise sum of
    two, then sum the unmarked integers up to the fixed bound 28123 (above which every integer
    is an abundant sum). O(n*sqrt(n)) to classify, O(a^2) marking."""
    limit = 28123
    abundant_numbers = [i for i in range(12, limit + 1) if sum_proper_divisors(i) > i]
    is_abundant_sum = [False] * (limit + 1)
    for i in range(len(abundant_numbers)):
        for j in range(i, len(abundant_numbers)):
            abundant_sum = abundant_numbers[i] + abundant_numbers[j]
            if abundant_sum > limit:
                break
            is_abundant_sum[abundant_sum] = True
    return str(sum((i for i in range(1, limit + 1) if not is_abundant_sum[i])))


if __name__ == "__main__":
    raise SystemExit(solve())
