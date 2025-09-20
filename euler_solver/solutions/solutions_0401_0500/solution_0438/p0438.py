#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 438: Integer Part of Polynomial Equation's Solutions.

Problem Statement:
    For an n-tuple of integers t = (a_1, ..., a_n), let (x_1, ..., x_n) be the
    solutions of the polynomial equation

        x^n + a_1 x^(n-1) + a_2 x^(n-2) + ... + a_(n-1) x + a_n = 0.

    Consider the following two conditions:
        1. x_1, ..., x_n are all real.
        2. If x_1, ..., x_n are sorted, floor(x_i) = i for 1 <= i <= n, where
           floor is the floor function.

    In the case of n = 4, there are 12 n-tuples of integers that satisfy both
    conditions.
    Define S(t) as the sum of the absolute values of the integers in t.
    For n = 4, the sum of S(t) over all such n-tuples t is 2087.

    Find the sum of S(t) for n = 7.

URL: https://projecteuler.net/problem=438
"""
from typing import Any

euler_problem: int = 438
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'n': 7}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
