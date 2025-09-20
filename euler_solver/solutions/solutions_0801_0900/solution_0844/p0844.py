#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 844: k-Markov Numbers.

Problem Statement:
    Consider positive integer solutions to
        a^2+b^2+c^2 = 3abc
    For example, (1,5,13) is a solution. We define a 3-Markov number to be any part
    of a solution, so 1, 5 and 13 are all 3-Markov numbers. Adding distinct 3-Markov
    numbers ≤ 10^3 would give 2797.

    Now we define a k-Markov number to be a positive integer that is part of a solution to:
        sum_{i=1}^k x_i^2 = k * product_{i=1}^k x_i,
        where x_i are positive integers.

    Let M_k(N) be the sum of k-Markov numbers ≤ N. Hence M_3(10^3)=2797, also
    M_8(10^8) = 131493335.

    Define S(K,N) = sum_{k=3}^K M_k(N). You are given S(4, 10^2)=229 and
    S(10, 10^8)=2383369980.

    Find S(10^{18}, 10^{18}). Give your answer modulo 1_405_695_061.

URL: https://projecteuler.net/problem=844
"""
from typing import Any

euler_problem: int = 844
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'K': 4, 'N': 100}, 'answer': None},
    {'category': 'main', 'input': {'K': 10, 'N': 100000000}, 'answer': None},
]
encrypted: str = (
    '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'
    '9cZKkv208eBSEJ6jfiOMD5+sjyM='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
