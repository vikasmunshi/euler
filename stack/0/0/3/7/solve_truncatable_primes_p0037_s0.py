#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Migrated from:
  file: euler_solver/solutions/solutions_0001_0100/solution_0037/p0037.py
  func: solve_truncatable_primes_p0037_s0
"""

from __future__ import annotations

from typing import Generator, List, Set


def primes_generator() -> Generator[int, None, None]:
    yield 2
    composites: dict[int, int] = {}
    n = 3
    while True:
        if n not in composites:
            yield n
            composites[n * n] = n
        else:
            p = composites.pop(n)
            m = n + 2 * p
            while m in composites:
                m += 2 * p
            composites[m] = p
        n += 2


def solve() -> int:
    primes: Set[str] = set()
    truncatable_primes: List[int] = list()
    for prime_num in primes_generator():
        prime = str(prime_num)
        primes.add(prime)
        if int(prime) < 10:
            continue
        if not any(
            (pl not in primes or pr not in primes for pl, pr in [(prime[i:], prime[:i]) for i in range(1, len(prime))])
        ):
            truncatable_primes.append(prime_num)
        if len(truncatable_primes) == 11:
            break
    return sum(truncatable_primes)


def main() -> int:
    print(solve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
