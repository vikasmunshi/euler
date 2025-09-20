#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 784: Reciprocal Pairs.

Problem Statement:
    Let's call a pair of positive integers p, q (p < q) reciprocal, if there is a
    positive integer r < p such that r equals both the inverse of p modulo q and
    the inverse of q modulo p.

    For example, (3,5) is one reciprocal pair for r=2.
    Let F(N) be the total sum of p+q for all reciprocal pairs (p,q) where p ≤ N.

    F(5) = 59 due to these four reciprocal pairs (3,5), (4,11), (5,7) and (5,19).
    You are also given F(10^2) = 697317.

    Find F(2·10^6).

URL: https://projecteuler.net/problem=784
"""
from typing import Any

euler_problem: int = 784
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 2000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'khMv6/kTlTEwpe6Odt+idTOBZzUZTA53qhgnSA=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
