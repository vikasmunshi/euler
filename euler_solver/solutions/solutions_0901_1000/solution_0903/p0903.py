#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 903: Total Permutation Powers.

Problem Statement:
    A permutation π of {1, ..., n} can be represented in one-line notation as
    π(1), ..., π(n). If all n! permutations are written in lexicographic order
    then rank(π) is the position of π in this 1-based list.

    For example, rank(2, 1, 3) = 3 because the six permutations of {1, 2, 3}
    in lexicographic order are:
    1, 2, 3
    1, 3, 2
    2, 1, 3
    2, 3, 1
    3, 1, 2
    3, 2, 1

    Let Q(n) be the sum sum_{π} sum_{i=1}^{n!} rank(π^i), where π ranges over all
    permutations of {1, ..., n}, and π^i is the permutation arising from applying
    π i times.

    For example, Q(2) = 5, Q(3) = 88, Q(6) = 133103808 and Q(10) ≡ 468421536
    (mod 10^9 + 7).

    Find Q(10^6). Give your answer modulo (10^9 + 7).

URL: https://projecteuler.net/problem=903
"""
from typing import Any

euler_problem: int = 903
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 2}, 'answer': None},
    {'category': 'dev', 'input': {'n': 3}, 'answer': None},
    {'category': 'main', 'input': {'n': 1000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
