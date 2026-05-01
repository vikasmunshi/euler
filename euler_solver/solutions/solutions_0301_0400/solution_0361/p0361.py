#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 361: Subsequence of Thue-Morse Sequence.

Problem Statement:
    The Thue-Morse sequence {T_n} is a binary sequence satisfying:
    T_0 = 0
    T_{2n} = T_n
    T_{2n + 1} = 1 - T_n

    The first several terms of {T_n} begin:
    01101001100101101001011001101001...

    Define {A_n} as the sorted sequence of integers whose binary
    representation appears as a contiguous subsequence in {T_n}.
    For example, 18 is 10010 in binary and 10010 appears in {T_n}
    (T_8 to T_12), so 18 is in {A_n}. 14 is 1110 which never appears
    in {T_n}, so 14 is not in {A_n}.

    The first terms of {A_n} are:
    A_0 = 0, A_1 = 1, A_2 = 2, A_3 = 3, A_4 = 4, A_5 = 5, A_6 = 6,
    A_7 = 9, A_8 = 10, A_9 = 11, A_10 = 12, A_11 = 13, A_12 = 18, ...

    It is known that A_100 = 3251 and A_1000 = 80852364498.

    Find the last 9 digits of sum_{k = 1}^{18} A_{10^k}.

URL: https://projecteuler.net/problem=361
"""
from typing import Any

euler_problem: int = 361
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'k_max': 2}, 'answer': None},
    {'category': 'main', 'input': {'k_max': 18}, 'answer': None},
    {'category': 'extra', 'input': {'k_max': 20}, 'answer': None},
]
encrypted: str = (
    '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'
    'UYnqF5bTlvm6Bg9anrEWNA=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
