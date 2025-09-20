#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 319: Bounded Sequences.

Problem Statement:
    Let x_1, x_2, ..., x_n be a sequence of length n such that:
    x_1 = 2
    for all 1 < i <= n: x_{i-1} < x_i
    for all i and j with 1 <= i, j <= n: (x_i)^j < (x_j + 1)^i

    There are only five such sequences of length 2, namely:
    {2,4}, {2,5}, {2,6}, {2,7} and {2,8}.
    There are 293 such sequences of length 5; three examples are:
    {2,5,11,25,55}, {2,6,14,36,88}, {2,8,22,64,181}.

    Let t(n) denote the number of such sequences of length n.
    You are given that t(10) = 86195 and t(20) = 5227991891.

    Find t(10^10) and give your answer modulo 10^9.

URL: https://projecteuler.net/problem=319
"""
from typing import Any

euler_problem: int = 319
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 2}, 'answer': None},
    {'category': 'main', 'input': {'n': 10000000000}, 'answer': None},
    {'category': 'extra', 'input': {'n': 20}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
