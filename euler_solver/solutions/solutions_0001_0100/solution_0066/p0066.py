#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 66: Diophantine Equation.

Problem Statement:
    Consider quadratic Diophantine equations of the form:
    x^2 - Dy^2 = 1

    For example, when D=13, the minimal solution in x is 649^2 - 13 x 180^2 = 1.

    It can be assumed that there are no solutions in positive integers when D is square.

    By finding minimal solutions in x for D = {2, 3, 5, 6, 7}, we obtain the following:
        3^2 - 2 x 2^2 = 1
        2^2 - 3 x 1^2 = 1
        9^2 - 5 x 4^2 = 1
        5^2 - 6 x 2^2 = 1
        8^2 - 7 x 3^2 = 1

    Hence, by considering minimal solutions in x for D ≤ 7, the largest x is obtained when D=5.

    Find the value of D ≤ 1000 in minimal solutions of x for which the largest value of x is obtained.

Solution Approach:
    Use the theory of Pell's equation and continued fraction expansions of sqrt(D).
    For each non-square D ≤ 1000, compute the minimal solution (x,y) using
    periodic continued fractions. Track the largest x of these minimal solutions.
    This approach uses number theory and efficient continued fraction expansions.
    Time complexity is roughly O(D * sqrt(D)) or better depending on implementation.

Answer: 661
URL: https://projecteuler.net/problem=66
"""
from __future__ import annotations

from fractions import Fraction
from math import floor, sqrt
from operator import itemgetter
from typing import Any, Tuple

from euler_solver.framework import evaluate, logger, register_solution

euler_problem: int = 66
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_d': 7}, 'answer': 5},
    {'category': 'main', 'input': {'max_d': 1000}, 'answer': 661},
    {'category': 'extra', 'input': {'max_d': 10000}, 'answer': 9949},
]


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


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_diophantine_equation_p0066_s0(*, max_d: int) -> int:
    return max(((find_fundamental_solution_to_pell_equation(d)[0], d) for d in range(2, max_d + 1) if
                sqrt(d).is_integer() is False), key=itemgetter(0))[-1]


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
