#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Migrated from:
  file: euler_solver/solutions/solutions_0001_0100/solution_0023/p0023.py
  func: solve_non_abundant_sums_p0023_s1
"""

from __future__ import annotations


def sum_proper_divisors(n: int) -> int:
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


def solve() -> int:
    limit = 28123
    abundant_numbers = [i for i in range(12, limit + 1) if sum_proper_divisors(i) > i]
    is_abundant_sum = [False] * (limit + 1)
    for i in range(len(abundant_numbers)):
        for j in range(i, len(abundant_numbers)):
            abundant_sum = abundant_numbers[i] + abundant_numbers[j]
            if abundant_sum > limit:
                break
            is_abundant_sum[abundant_sum] = True
    return sum((i for i in range(1, limit + 1) if not is_abundant_sum[i]))


def main() -> int:
    print(solve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
