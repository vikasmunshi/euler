#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 840: Sum of Products.

Problem Statement:
    A partition of n is a set of positive integers for which the sum equals n.
    The partitions of 5 are:
    {5},{1,4},{2,3},{1,1,3},{1,2,2},{1,1,1,2} and {1,1,1,1,1}.

    Further we define the function D(p) as:
        D(1) = 1
        D(p) = 1, for any prime p
        D(pq) = D(p)q + pD(q), for any positive integers p,q > 1.

    Now let {a_1, a_2, ..., a_k} be a partition of n.
    We assign to this particular partition the value:
        P = product from j=1 to k of D(a_j).

    G(n) is the sum of P for all partitions of n.
    We can verify that G(10) = 164.

    We also define:
        S(N) = sum from n=1 to N of G(n).
    You are given S(10) = 396.
    Find S(5 * 10^4) mod 999676999.

URL: https://projecteuler.net/problem=840
"""
from typing import Any

euler_problem: int = 840
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'max_limit': 50000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
