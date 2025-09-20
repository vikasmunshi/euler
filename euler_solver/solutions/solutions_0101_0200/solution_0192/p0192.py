#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 192: Best Approximations.

Problem Statement:
    Let x be a real number.
    A best approximation to x for the denominator bound d is a rational number
    r/s in reduced form, with s <= d, such that any rational number which is
    closer to x than r/s has a denominator larger than d:
    |p/q - x| < |r/s - x| => q > d

    For example, the best approximation to sqrt(13) for the denominator bound
    20 is 18/5 and the best approximation to sqrt(13) for the denominator
    bound 30 is 101/28.

    Find the sum of all denominators of the best approximations to sqrt(n)
    for the denominator bound 10^12, where n is not a perfect square and
    1 < n <= 100000.

URL: https://projecteuler.net/problem=192
"""
from typing import Any

euler_problem: int = 192
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10, 'denominator_bound': 1000}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 100000, 'denominator_bound': 1000000000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'PLeMGvHL++P767B4xuwQrW3hsTw6/F+y'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
