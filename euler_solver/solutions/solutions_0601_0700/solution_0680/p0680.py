#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 680: Yarra Gnisrever.

Problem Statement:
    Let N and K be two positive integers.

    F_n is the n-th Fibonacci number: F_1 = F_2 = 1, F_n = F_{n - 1} + F_{n - 2} for all n >= 3.
    Let s_n = F_{2n - 1} mod N and let t_n = F_{2n} mod N.

    Start with an array of integers A = (A[0], ..., A[N - 1]) where initially every A[i] is equal to i.
    Now perform K successive operations on A, where the j-th operation consists of reversing the
    order of those elements in A with indices between s_j and t_j (both ends inclusive).

    Define R(N,K) to be sum over i=0 to N-1 of i * A[i] after K operations.

    For example, R(5, 4) = 27, as can be seen from the following procedure:

    Initial position: (0, 1, 2, 3, 4)
    Step 1 - Reverse A[1] to A[1]: (0, 1, 2, 3, 4)
    Step 2 - Reverse A[2] to A[3]: (0, 1, 3, 2, 4)
    Step 3 - Reverse A[0] to A[3]: (2, 3, 1, 0, 4)
    Step 4 - Reverse A[3] to A[1]: (2, 0, 1, 3, 4)
    R(5, 4) = 0*2 + 1*0 + 2*1 + 3*3 + 4*4 = 27

    Also, R(10^2, 10^2) = 246597 and R(10^4, 10^4) = 249275481640.

    Find R(10^18, 10^6) giving your answer modulo 10^9.

URL: https://projecteuler.net/problem=680
"""
from typing import Any

euler_problem: int = 680
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10, 'operations': 5}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 1000000000000000000, 'operations': 1000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
