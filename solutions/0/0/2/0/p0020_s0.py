#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 20: Factorial Digit Sum [Level 0]. """
from __future__ import annotations

import math

from solver.runners import runner


@runner.main
def solve(*args: str) -> str:
    """Sum the decimal digits of n! computed with Python's built-in arbitrary-precision int;
    n! has O(n log n) digits (Stirling), so the digit sum is linear in that size."""
    n = runner.parse_int(args[0])

    return str(sum((int(d) for d in str(math.factorial(n)))))


if __name__ == "__main__":
    raise SystemExit(solve())
