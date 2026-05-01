#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 921: Golden Recurrence.

Problem Statement:
    Consider the following recurrence relation:
        a_0 = (sqrt 5 + 1) / 2
        a_{n+1} = a_n(a_n^4 + 10 a_n^2 + 5) / (5 a_n^4 + 10 a_n^2 + 1)

    Note that a_0 is the golden ratio.

    a_n can always be written in the form (p_n sqrt 5 + 1) / q_n, where p_n and q_n
    are positive integers.

    Let s(n) = p_n^5 + q_n^5. So, s(0) = 1^5 + 2^5 = 33.

    The Fibonacci sequence is defined as: F_1=1, F_2=1, F_n=F_{n-1}+F_{n-2} for n > 2.

    Define S(m) = sum from i=2 to m of s(F_i).

    Find S(1618034). Submit your answer modulo 398874989.

URL: https://projecteuler.net/problem=921
"""
from typing import Any

euler_problem: int = 921
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'m': 1618034}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
