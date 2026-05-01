#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 697: Randomly Decaying Sequence.

Problem Statement:
    Given a fixed real number c, define a random sequence (X_n)_{n≥0} by the following
    random process:
        - X_0 = c (with probability 1).
        - For n > 0, X_n = U_n X_{n-1} where U_n is a real number chosen at random
          between zero and one, uniformly, and independently of all previous choices
          (U_m)_{m<n}.

    If we desire there to be precisely a 25% probability that X_100 < 1, then this can
    be arranged by fixing c such that log_10 c ≈ 46.27.

    Suppose now that c is set to a different value, so that there is precisely a 25%
    probability that X_10,000,000 < 1.

    Find log_10 c and give your answer rounded to two places after the decimal point.

URL: https://projecteuler.net/problem=697
"""
from typing import Any

euler_problem: int = 697
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 100}, 'answer': None},
    {'category': 'main', 'input': {'n': 10000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'veT2x7omvI2MbDnn2PilTiZ5cQeGzilS'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
