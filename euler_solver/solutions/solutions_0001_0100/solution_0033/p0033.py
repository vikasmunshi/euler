#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 33: Digit Cancelling Fractions.

Problem Statement:
    The fraction 49/98 is a curious fraction, as an inexperienced mathematician in
    attempting to simplify it may incorrectly believe that 49/98 = 4/8, which is correct,
    is obtained by cancelling the 9s.

    We shall consider fractions like, 30/50 = 3/5, to be trivial examples.

    There are exactly four non-trivial examples of this type of fraction, less than one
    in value, and containing two digits in the numerator and denominator.

    If the product of these four fractions is given in its lowest common terms, find the
    value of the denominator.

Solution Approach:
    Use brute force search on all two-digit numerator and denominator pairs less than 1.
    Check the digit cancelling condition for non-trivial cases. Multiply the fractions.
    Reduce the product to lowest terms using gcd and return the denominator.
    Time complexity O(1) given fixed digit size; simple number theory and gcd application.

Answer: 100
URL: https://projecteuler.net/problem=33
"""
from __future__ import annotations

from fractions import Fraction
from functools import reduce
from typing import Any

from euler_solver.framework import evaluate, logger, register_solution

euler_problem: int = 33
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}, 'answer': 100},
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_digit_cancelling_fractions_p0033_s0() -> int:
    return reduce(lambda a, b: a * b, (Fraction(numerator, denominator) for denominator in range(2, 10)
                                       for numerator in range(1, denominator)
                                       for x in range(1, 10)
                                       if denominator != x != numerator
                                       if (10 * numerator + x) * denominator == (10 * x + denominator) * numerator),
                  Fraction(1, 1)).denominator


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
