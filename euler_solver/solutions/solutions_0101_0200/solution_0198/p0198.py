#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 198: Ambiguous Numbers.

Problem Statement:
    A best approximation to a real number x for the denominator bound d is a
    rational number r/s (in reduced form) with s <= d, so that any rational
    p/q which is closer to x than r/s has q > d.

    Usually the best approximation to a real number is uniquely determined for
    all denominator bounds. However, there are exceptions, e.g. 9/40 has the
    two best approximations 1/4 and 1/5 for the denominator bound 6.

    We shall call a real number x ambiguous if there is at least one denominator
    bound for which x possesses two best approximations. Clearly, an
    ambiguous number is necessarily rational.

    How many ambiguous numbers x = p/q, 0 < x < 1/100, are there whose
    denominator q does not exceed 10^8?

URL: https://projecteuler.net/problem=198
"""
from typing import Any

euler_problem: int = 198
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 1000}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 100000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'uXlJxaRgmew='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
