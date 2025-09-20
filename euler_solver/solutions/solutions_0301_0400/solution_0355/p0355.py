#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 355: Maximal Coprime Subset.

Problem Statement:
    Define Co(n) to be the maximal possible sum of a set of mutually
    co-prime elements from {1,2,...,n}. For example Co(10) is 30 and hits
    that maximum on the subset {1,5,7,8,9}.

    You are given that Co(30) = 193 and Co(100) = 1356.

    Find Co(200000).

URL: https://projecteuler.net/problem=355
"""
from typing import Any

euler_problem: int = 355
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 200000}, 'answer': None},
    {'category': 'extra', 'input': {'max_limit': 1000000}, 'answer': None},
]
encrypted: str = (
    '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'
    '/4XL+iNwg1s/DRaIvajH2xUA43g='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
