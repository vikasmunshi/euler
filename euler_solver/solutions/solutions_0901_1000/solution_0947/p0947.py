#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 947: Fibonacci Residues.

Problem Statement:
    The (a,b,m)-sequence, where 0 <= a,b < m, is defined as

        g(0) = a
        g(1) = b
        g(n) = (g(n-1) + g(n-2)) mod m

    All (a,b,m)-sequences are periodic with period denoted by p(a,b,m).
    The first few terms of the (0,1,8)-sequence are
    (0,1,1,2,3,5,0,5,5,2,7,1,0,1,1,2,...) and so p(0,1,8) = 12.

    Let s(m) = sum from a=0 to m-1 and b=0 to m-1 of (p(a,b,m))^2.
    For example, s(3) = 513 and s(10) = 225820.

    Define S(M) = sum from m=1 to M of s(m).
    You are given S(3) = 542 and S(10) = 310897.

    Find S(10^6). Give your answer modulo 999999893.

URL: https://projecteuler.net/problem=947
"""
from typing import Any

euler_problem: int = 947
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 1000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
