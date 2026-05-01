#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 834: Add and Divide.

Problem Statement:
    A sequence is created by starting with a positive integer n and incrementing by
    (n+m) at the m-th step. If n=10, the resulting sequence will be
    21, 33, 46, 60, 75, 91, 108, 126, ...

    Let S(n) be the set of indices m, for which the m-th term in the sequence is divisible
    by (n+m).
    For example, S(10)={5,8,20,35,80}.

    Define T(n) to be the sum of the indices in S(n). For example, T(10) = 148 and T(10^2)=21828.

    Let U(N)=∑_{n=3}^N T(n).
    You are given, U(10^2)=612572.

    Find U(1234567).

URL: https://projecteuler.net/problem=834
"""
from typing import Any

euler_problem: int = 834
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 100}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 1234567}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
