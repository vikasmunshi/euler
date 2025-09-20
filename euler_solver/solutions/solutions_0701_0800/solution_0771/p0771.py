#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 771: Pseudo Geometric Sequences.

Problem Statement:
    We define a pseudo-geometric sequence to be a finite sequence a_0, a_1, ..., a_n
    of positive integers, satisfying the following conditions:

        n >= 4, i.e. the sequence has at least 5 terms.
        0 < a_0 < a_1 < ... < a_n, i.e. the sequence is strictly increasing.
        | a_i^2 - a_{i-1} a_{i+1} | <= 2 for 1 <= i <= n-1.

    Let G(N) be the number of different pseudo-geometric sequences whose terms do not
    exceed N.

    For example, G(6) = 4, as the following 4 sequences give a complete list:
        1, 2, 3, 4, 5
        1, 2, 3, 4, 6
        2, 3, 4, 5, 6
        1, 2, 3, 4, 5, 6

    Also, G(10) = 26, G(100) = 4710 and G(1000) = 496805.

    Find G(10^18). Give your answer modulo 1,000,000,007.

URL: https://projecteuler.net/problem=771
"""
from typing import Any

euler_problem: int = 771
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 1000000000000000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
