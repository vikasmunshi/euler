#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 606: Gozinta Chains II.

Problem Statement:
    A gozinta chain for n is a sequence {1, a, b, ..., n} where each element
    properly divides the next.

    For example, there are eight distinct gozinta chains for 12:
    {1,12}, {1,2,12}, {1,2,4,12}, {1,2,6,12}, {1,3,12}, {1,3,6,12}, {1,4,12}
    and {1,6,12}.

    Let S(n) be the sum of all numbers, k, not exceeding n, which have 252 distinct
    gozinta chains.

    You are given S(10^6) = 8462952 and S(10^12) = 623291998881978.

    Find S(10^36), giving the last nine digits of your answer.

URL: https://projecteuler.net/problem=606
"""
from typing import Any

euler_problem: int = 606
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 1000}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 1000000}, 'answer': None},
    {'category': 'extra', 'input': {'max_limit': 1000000000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
