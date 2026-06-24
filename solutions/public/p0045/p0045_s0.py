#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 45: Triangular, Pentagonal, and Hexagonal [Level 1]. """
from __future__ import annotations

from solver.runners import runner


@runner.main
def solve(*args: str) -> str:
    """Scan triangular numbers T(n) from a given index, keeping those whose inverse pentagonal and
    triangular discriminants are perfect squares (root == 5 mod 6 and 3 mod 4); O(k) candidates."""
    n = runner.parse_int(args[0])

    while n := (n + 1):
        triangular_number = n * (n + 1) // 2
        if (1 + 24 * triangular_number) ** 0.5 % 6 == 5.0:
            if (1 + 8 * triangular_number) ** 0.5 % 4 == 3.0:
                return str(triangular_number)
    else:
        raise ValueError("No solution found")


if __name__ == "__main__":
    raise SystemExit(solve())
