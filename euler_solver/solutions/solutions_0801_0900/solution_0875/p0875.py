#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 875: Quadruple Congruence.

Problem Statement:
    For a positive integer n we define q(n) to be the number of solutions to:

    a_1^2 + a_2^2 + a_3^2 + a_4^2 ≡ b_1^2 + b_2^2 + b_3^2 + b_4^2 (mod n)

    where 0 ≤ a_i, b_i < n. For example, q(4) = 18432.

    Define Q(n) = sum of q(i) for i from 1 to n. You are given Q(10) = 18573381.

    Find Q(12345678). Give your answer modulo 1001961001.

URL: https://projecteuler.net/problem=875
"""
from typing import Any

euler_problem: int = 875
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 12345678}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
