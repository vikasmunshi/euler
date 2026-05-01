#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Migrated from:
  file: euler_solver/solutions/solutions_0001_0100/solution_0035/p0035.py
  func: solve_circular_primes_p0035_s1_pps
"""

from __future__ import annotations

from bisect import bisect_right
from sys import argv
from typing import Set

import pyprimesieve as pps


def get_primes_from_pps(max_limit: int) -> list[int]:
    all_primes = pps.primes(max(max_limit, 10**6))
    return all_primes[: bisect_right(all_primes, max_limit)]


def get_rotated_numbers(*, num: int) -> Set[int]:
    str_num: str = str(num)
    return {num} if len(str_num) == 1 else {int(str_num[i:] + str_num[:i]) for i in range(1, len(str_num) + 1)}


def solve(*, max_limit: int) -> int:
    primes = set(get_primes_from_pps(max_limit))
    circular_primes = [
        prime
        for prime in primes
        if prime < 10
        or (
            not any((d in str(prime) for d in "024568"))
            and (not any((rotated_number not in primes for rotated_number in get_rotated_numbers(num=prime))))
        )
    ]
    return len(circular_primes)


def main() -> int:
    print(solve(max_limit=int(argv[1])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
