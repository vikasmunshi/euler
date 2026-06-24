#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 66: Diophantine Equation [Level 11]. """
from __future__ import annotations

import fractions
import math
import operator

from solver.runners import runner


def compute_nth_convergent(continued_fraction: tuple[int, ...], n: int) -> fractions.Fraction:
    """Evaluate the n-th convergent backward (innermost term first), cycling the periodic part."""
    period_length: int = len(continued_fraction) - 1
    convergent: fractions.Fraction = fractions.Fraction(continued_fraction[(n - 1) % period_length + 1], 1)
    for i in range(n - 1, 0, -1):
        term_index = (i - 1) % period_length + 1
        term = fractions.Fraction(continued_fraction[term_index], 1)
        convergent = term + fractions.Fraction(1, convergent)
    convergent = fractions.Fraction(continued_fraction[0], 1) + fractions.Fraction(1, convergent)
    return convergent


def find_fundamental_solution_to_pell_equation(d: int) -> tuple[int, int]:
    """Fundamental (x, y) via convergents of sqrt(d): index 2*L-3 if period L is even, else L-2."""
    if (sqrt_d := math.sqrt(d)).is_integer():
        return (1, 0)
    continued_fraction: tuple[int, ...] = (math.floor(sqrt_d),)
    m: int = 0
    n: int = 1
    while continued_fraction[-1] != 2 * continued_fraction[0]:
        m = n * continued_fraction[-1] - m
        n = (d - m * m) // n
        continued_fraction += (math.floor((sqrt_d + m) / n),)
    if (len_continued_fraction := len(continued_fraction)) % 2 == 0:
        return compute_nth_convergent(continued_fraction, 2 * len_continued_fraction - 3).as_integer_ratio()
    else:
        return compute_nth_convergent(continued_fraction, len_continued_fraction - 2).as_integer_ratio()


@runner.main
def solve(*args: str) -> str:
    """Maximise the fundamental Pell x over non-square D <= max_d using continued-fraction
    convergents of sqrt(D); O(max_d * sqrt(max_d)) big-integer operations."""
    max_d = runner.parse_int(args[0])

    return str(max(
        (
            (find_fundamental_solution_to_pell_equation(d)[0], d)
            for d in range(2, max_d + 1)
            if math.sqrt(d).is_integer() is False
        ),
        key=operator.itemgetter(0),
    )[-1])


if __name__ == "__main__":
    raise SystemExit(solve())
