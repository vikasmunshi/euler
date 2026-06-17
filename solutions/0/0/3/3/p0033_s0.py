#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 33: Digit Cancelling Fractions [Level 1]. """
from __future__ import annotations

import fractions
import functools

from solver.runners import runner


@runner.main
def solve(*args: str) -> str:
    """Brute-force the digit-cancelling pairs via the cross-multiplied integer identity
    (10*numerator + x) * denominator == (10*x + denominator) * numerator (no floating point),
    folding the matches as exact Fractions; the answer is the reduced product's denominator; O(1)."""
    return str(functools.reduce(
        lambda a, b: a * b,
        (
            fractions.Fraction(numerator, denominator)
            for denominator in range(2, 10)
            for numerator in range(1, denominator)
            for x in range(1, 10)
            if denominator != x != numerator
            if (10 * numerator + x) * denominator == (10 * x + denominator) * numerator
        ),
        fractions.Fraction(1, 1),
    ).denominator)


if __name__ == "__main__":
    raise SystemExit(solve())
