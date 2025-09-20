#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 858: LCM.

Problem Statement:
    Define G(N) = sum of lcm(S) where S ranges through all subsets of {1, ..., N} and lcm
    denotes the lowest common multiple. Note that the lcm of the empty set is 1.

    You are given G(5) = 528 and G(20) = 8463108648960.

    Find G(800). Give your answer modulo 10^9 + 7.

URL: https://projecteuler.net/problem=858
"""
from typing import Any

euler_problem: int = 858
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 5}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 800}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
