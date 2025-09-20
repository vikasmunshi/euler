#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 720: Unpredictable Permutations.

Problem Statement:
    Consider all permutations of {1, 2, ..., N}, listed in lexicographic order.
    For example, for N=4, the list starts as follows:

        (1, 2, 3, 4)
        (1, 2, 4, 3)
        (1, 3, 2, 4)
        (1, 3, 4, 2)
        (1, 4, 2, 3)
        (1, 4, 3, 2)
        (2, 1, 3, 4)
        ...

    Let us call a permutation P unpredictable if there is no choice of three indices
    i < j < k such that P(i), P(j) and P(k) constitute an arithmetic progression.
    For example, P = (3, 4, 2, 1) is not unpredictable because P(1), P(3), P(4) is
    an arithmetic progression.

    Let S(N) be the position within the list of the first unpredictable permutation.

    For example, given N = 4, the first unpredictable permutation is (1, 3, 2, 4) so
    S(4) = 3.
    You are also given that S(8) = 2295 and S(32) ≡ 641839205 (mod 1,000,000,007).

    Find S(2^25). Give your answer modulo 1,000,000,007.

URL: https://projecteuler.net/problem=720
"""
from typing import Any

euler_problem: int = 720
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 4}, 'answer': None},
    {'category': 'main', 'input': {'n': 33554432}, 'answer': None},
]
encrypted: str = (
    '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'
    'dbv6bt0WsIMuGA2sk+Bv7BJ00DUfm3uihVmdAw=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
