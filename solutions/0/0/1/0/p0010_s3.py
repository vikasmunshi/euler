#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 10: Summation of Primes [Level 0]. """
from __future__ import annotations

from solver.runners import runner


def is_prime(num: int) -> bool:
    """Test primality by trial division of odd divisors up to sqrt(num)."""
    if num < 2:
        return False
    if num == 2:
        return True
    if num % 2 == 0:
        return False
    i = 3
    while i * i <= num:
        if num % i == 0:
            return False
        i += 2
    return True


@runner.main
def solve(*args: str) -> str:
    """Sum primes below max_num by trial-division primality test on each candidate; O(n*sqrt(n)/log n)."""
    max_num = runner.parse_int(args[0])

    return str(sum((n for n in range(2, max_num) if is_prime(n))))


if __name__ == "__main__":
    raise SystemExit(solve())
