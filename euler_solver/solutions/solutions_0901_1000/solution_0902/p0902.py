#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 902: Permutation Powers.

Problem Statement:
    A permutation π of {1, ..., n} can be represented in one-line notation as
    π(1), ..., π(n). If all n! permutations are written in lexicographic order
    then rank(π) is the position of π in this 1-based list.

    For example, rank(2,1,3) = 3 because the six permutations of {1, 2, 3} in
    lexicographic order are:
    1, 2, 3   1, 3, 2   2, 1, 3   2, 3, 1   3, 1, 2   3, 2, 1

    For a positive integer m, define the permutation of {1, ..., n} with n = m(m+1)/2:
        σ(i) = k(k−1)/2 + 1 if i = k(k+1)/2 for k in {1, ..., m};
               i + 1 otherwise;
        τ(i) = ((10^9 + 7) * i mod n) + 1
        π(i) = τ⁻¹(σ(τ(i))) where τ⁻¹ is the inverse of τ.

    Define P(m) = sum_{k=1}^{m!} rank(π^k), where π^k is π applied k times.
    Examples: P(2) = 4, P(3) = 780, P(4) = 38810300.

    Find P(100). Give the answer modulo 10^9 + 7.

URL: https://projecteuler.net/problem=902
"""
from typing import Any

euler_problem: int = 902
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}, 'answer': None},
]
encrypted: str = (
    '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'
    'M80S/K7h1tnNxz9r'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
