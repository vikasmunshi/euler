#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 729: Range of Periodic Sequence.

Problem Statement:
    Consider the sequence of real numbers a_n defined by the starting value a_0 and
    the recurrence a_(n+1) = a_n - 1 / a_n for any n >= 0.

    For some starting values a_0 the sequence will be periodic. For example, a_0 = sqrt(1/2)
    yields the sequence: sqrt(1/2), -sqrt(1/2), sqrt(1/2), ...

    We are interested in the range of such a periodic sequence which is the difference
    between the maximum and minimum of the sequence. For example, the range of the sequence
    above would be sqrt(1/2) - (-sqrt(1/2)) = sqrt(2).

    Let S(P) be the sum of the ranges of all such periodic sequences with a period not
    exceeding P. For example, S(2) = 2 * sqrt(2) ≈ 2.8284, being the sum of the ranges
    of the two sequences starting with a_0 = sqrt(1/2) and a_0 = -sqrt(1/2).
    You are given S(3) ≈ 14.6461 and S(5) ≈ 124.1056.

    Find S(25), rounded to 4 decimal places.

URL: https://projecteuler.net/problem=729
"""
from typing import Any

euler_problem: int = 729
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_period': 3}, 'answer': None},
    {'category': 'main', 'input': {'max_period': 25}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
