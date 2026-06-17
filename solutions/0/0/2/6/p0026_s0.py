#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 26: Reciprocal Cycles [Level 2]. """
from __future__ import annotations

import math

from solver.runners import runner


def multiplicative_order(a: int, modulus: int) -> int | None:
    """Smallest k with a**k ≡ 1 (mod modulus), or None if a is not coprime to modulus."""
    r = 1
    for k in range(1, modulus):
        r = r * a % modulus
        if r == 1:
            return k
    else:
        return None


@runner.main
def solve(*args: str) -> str:
    """The recurring-cycle length of 1/d equals the multiplicative order of 10 modulo d
    (for d coprime to 10); return the d below the limit that maximises it. Since that order
    is < d, only the top window of denominators can win, so just those are scanned. O(limit^2)."""
    limit = runner.parse_int(args[0])

    return str(max(
        (
            (multiplicative_order(a=10, modulus=d), d)
            for i in range(max(limit // 10, 10))
            if (d := (limit - i)) > 6 and math.gcd(d, 10) == 1
        )
    )[1])


if __name__ == "__main__":
    raise SystemExit(solve())
