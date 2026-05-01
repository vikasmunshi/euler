#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 254: Sums of Digit Factorials.

Problem Statement:
    Define f(n) as the sum of the factorials of the digits of n. For example,
    f(342) = 3! + 4! + 2! = 32.

    Define sf(n) as the sum of the digits of f(n). So sf(342) = 3 + 2 = 5.

    Define g(i) to be the smallest positive integer n such that sf(n) = i.
    Though sf(342) is 5, sf(25) is also 5, and it can be verified that g(5)
    is 25.

    Define sg(i) as the sum of the digits of g(i). So sg(5) = 2 + 5 = 7.

    Further, it can be verified that g(20) is 267 and sum sg(i) for 1 <= i <= 20
    is 156.

    What is sum sg(i) for 1 <= i <= 150?

URL: https://projecteuler.net/problem=254
"""
from typing import Any

euler_problem: int = 254
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_i': 20}, 'answer': None},
    {'category': 'main', 'input': {'max_i': 150}, 'answer': None},
    {'category': 'extra', 'input': {'max_i': 500}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
