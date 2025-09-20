#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 940: Two-Dimensional Recurrence.

Problem Statement:
    The Fibonacci sequence (f_i) is the unique sequence such that
        f_0 = 0
        f_1 = 1
        f_{i+1} = f_i + f_{i-1}

    Similarly, there is a unique function A(m,n) such that:
        A(0,0) = 0
        A(0,1) = 1
        A(m+1,n) = A(m,n+1) + A(m,n)
        A(m+1,n+1) = 2A(m+1,n) + A(m,n)

    Define S(k) = sum_{i=2}^k sum_{j=2}^k A(f_i, f_j).

    For example:
        S(3) = A(1,1) + A(1,2) + A(2,1) + A(2,2)
             = 2 + 5 + 7 + 16
             = 30

    You are also given S(5) = 10396.

    Find S(50), giving your answer modulo 1123581313.

URL: https://projecteuler.net/problem=940
"""
from typing import Any

euler_problem: int = 940
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'k': 3}, 'answer': None},
    {'category': 'main', 'input': {'k': 50}, 'answer': None},
]
encrypted: str = (
    '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'
    'XscncRd52shXA9lppT6vbm/P5E8='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
