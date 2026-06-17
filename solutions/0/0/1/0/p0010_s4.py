#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 10: Summation of Primes [Level 0]. """
from __future__ import annotations

import primesieve
from solver.runners import runner


@runner.main
def solve(*args: str) -> str:
    """Sum primes below max_num via the primesieve library's optimised wheel-factorised sieve; ~O(n)."""
    max_num = runner.parse_int(args[0])

    return str(int(sum(primesieve.primes(max_num - 1))))


if __name__ == "__main__":
    raise SystemExit(solve())
