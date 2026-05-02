#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Migrated from:
  file: euler_solver/solutions/solutions_0001_0100/solution_0066/p0066.py
  func: solve_diophantine_equation_p0066_s0
"""

from __future__ import annotations

from fractions import Fraction
from math import floor, sqrt
from operator import itemgetter
from sys import argv
from typing import Tuple


def compute_nth_convergent(continued_fraction: Tuple[int, ...], n: int) -> Fraction:
    period_length: int = len(continued_fraction) - 1
    convergent: Fraction = Fraction(continued_fraction[(n - 1) % period_length + 1], 1)
    for i in range(n - 1, 0, -1):
        term_index = (i - 1) % period_length + 1
        term = Fraction(continued_fraction[term_index], 1)
        convergent = term + Fraction(1, convergent)
    convergent = Fraction(continued_fraction[0], 1) + Fraction(1, convergent)
    return convergent


def find_fundamental_solution_to_pell_equation(d: int) -> Tuple[int, int]:
    if (sqrt_d := sqrt(d)).is_integer():
        return (1, 0)
    continued_fraction: Tuple[int, ...] = (floor(sqrt_d),)
    m: int = 0
    n: int = 1
    while continued_fraction[-1] != 2 * continued_fraction[0]:
        m = n * continued_fraction[-1] - m
        n = (d - m * m) // n
        continued_fraction += (floor((sqrt_d + m) / n),)
    if (len_continued_fraction := len(continued_fraction)) % 2 == 0:
        return compute_nth_convergent(continued_fraction, 2 * len_continued_fraction - 3).as_integer_ratio()
    else:
        return compute_nth_convergent(continued_fraction, len_continued_fraction - 2).as_integer_ratio()


def solve(*, max_d: int) -> int:
    return max(
        (
            (find_fundamental_solution_to_pell_equation(d)[0], d)
            for d in range(2, max_d + 1)
            if sqrt(d).is_integer() is False
        ),
        key=itemgetter(0),
    )[-1]


def main() -> int:
    print(solve(max_d=int(argv[1])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
