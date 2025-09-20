#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 548: Gozinta Chains.

Problem Statement:
    A gozinta chain for n is a sequence {1,a,b,...,n} where each element properly
    divides the next.
    There are eight gozinta chains for 12:
    {1,12}, {1,2,12}, {1,2,4,12}, {1,2,6,12}, {1,3,12}, {1,3,6,12}, {1,4,12} and {1,6,12}.
    Let g(n) be the number of gozinta chains for n, so g(12)=8.
    g(48)=48 and g(120)=132.

    Find the sum of the numbers n not exceeding 10^16 for which g(n)=n.

URL: https://projecteuler.net/problem=548
"""
from typing import Any

euler_problem: int = 548
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}, 'answer': None},
]
encrypted: str = (
    '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'
    'vbPHwaYco19DAytfdlYaOpfpjKIY+cpm4MTeiQ=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
