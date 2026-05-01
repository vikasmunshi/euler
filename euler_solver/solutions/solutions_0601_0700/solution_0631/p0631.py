#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 631: Constrained Permutations.

Problem Statement:
    Let (p_1 p_2 ... p_k) denote the permutation of the set {1, ..., k} that maps p_i to i.
    Define the length of the permutation to be k; note that the empty permutation () has length zero.

    Define an occurrence of a permutation p = (p_1 p_2 ... p_k) in a permutation P = (P_1 P_2 ... P_n)
    to be a sequence 1 ≤ t_1 < t_2 < ... < t_k ≤ n such that p_i < p_j if and only if P_{t_i} < P_{t_j}
    for all i,j in {1, ..., k}.

    For example, (1243) occurs twice in the permutation (314625):
    once as the 1st, 3rd, 4th and 6th elements (3 4 6 5),
    and once as the 2nd, 3rd, 4th and 6th elements (1 4 6 5).

    Let f(n, m) be the number of permutations P of length at most n such that there is no occurrence
    of the permutation 1243 in P and there are at most m occurrences of the permutation 21 in P.

    For example, f(2, 0) = 3, with the permutations (), (1), (1,2) but not (2,1).

    You are also given that f(4, 5) = 32 and f(10, 25) = 294400.

    Find f(10^18, 40) modulo 1000000007.

URL: https://projecteuler.net/problem=631
"""
from typing import Any

euler_problem: int = 631
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 2, 'm': 0}, 'answer': None},
    {'category': 'main', 'input': {'n': 1000000000000000000, 'm': 40}, 'answer': None},
    {'category': 'extra', 'input': {'n': 1000000000000000000, 'm': 50}, 'answer': None},
]
encrypted: str = (
    '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'
    'Xvrq4jag5W8='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
