#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 48: Self Powers [Level 0]. """
from __future__ import annotations

from solver.runners import runner


@runner.main
def solve(*args: str) -> str:
    """Sum i**i mod 10**10 via three-argument pow (modular exponentiation); O(N log N)."""
    limit = runner.parse_int(args[0])

    modulo: int = 10**10
    result: int = 0
    for i in range(1, limit + 1):
        term = pow(i, i, modulo)
        result = (result + term) % modulo
    return str(result)


if __name__ == "__main__":
    raise SystemExit(solve())
