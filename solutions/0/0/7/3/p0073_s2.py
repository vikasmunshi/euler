#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 73: Counting Fractions in a Range [Level 3]. """
from __future__ import annotations

from solver.runners import runner


@runner.main
def solve(*args: str) -> str:
    """Count fractions in (1/3, 1/2) as a Farey rank difference: rank(1/2) - rank(1/3) - 1 (the -1
    drops 1/2 itself), each rank computed by an O(max_d log max_d) additive Mobius sieve."""
    max_d = runner.parse_int(args[0])

    def rank(n: int, d: int) -> int:
        """Reduced fractions with denominator <= max_d that are <= n/d, via an additive Mobius
        sieve: data[i] = floor(i*n/d) counts all such fractions, then subtracting each data[i]
        from its multiples leaves the exact coprime count per denominator; their sum is the rank."""
        len_data: int = max_d + 1
        data: list[int] = [i * n // d for i in range(len_data)]
        for i in range(1, len_data):
            for j in range(2 * i, len_data, i):
                data[j] -= data[i]
        return sum(data)

    return str(rank(n=1, d=2) - rank(n=1, d=3) - 1)


if __name__ == "__main__":
    raise SystemExit(solve())
