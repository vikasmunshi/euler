#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 282: The Ackermann Function.

Problem Statement:
    For non-negative integers m, n, the Ackermann function A(m,n) is
    defined as follows:

    A(m,n) =
        n+1                              if m = 0
        A(m-1,1)                         if m > 0 and n = 0
        A(m-1, A(m,n-1))                 if m > 0 and n > 0

    For example A(1,0) = 2, A(2,2) = 7 and A(3,4) = 125.

    Find sum_{n=0}^6 A(n,n) and give your answer mod 14^8.

URL: https://projecteuler.net/problem=282
"""
from typing import Any

euler_problem: int = 282
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_n': 2, 'modulo': 1475789056}, 'answer': None},
    {'category': 'main', 'input': {'max_n': 6, 'modulo': 1475789056}, 'answer': None},
    {'category': 'extra', 'input': {'max_n': 7, 'modulo': 1475789056}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
