#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 537: Counting Tuples.

Problem Statement:
    Let pi(x) be the prime counting function, i.e. the number of prime numbers less
    than or equal to x.
    For example, pi(1)=0, pi(2)=1, pi(100)=25.

    Let T(n, k) be the number of k-tuples (x_1, ..., x_k) which satisfy:
    1. every x_i is a positive integer;
    2. sum of pi(x_i) from i=1 to k equals n.

    For example T(3,3) = 19.
    The 19 tuples are (1,1,5), (1,5,1), (5,1,1), (1,1,6), (1,6,1), (6,1,1),
    (1,2,3), (1,3,2), (2,1,3), (2,3,1), (3,1,2), (3,2,1), (1,2,4), (1,4,2),
    (2,1,4), (2,4,1), (4,1,2), (4,2,1), (2,2,2).

    You are given T(10, 10) = 869985 and T(10^3, 10^3) ≡ 578270566 modulo 1004535809.

    Find T(20000, 20000) modulo 1004535809.

URL: https://projecteuler.net/problem=537
"""
from typing import Any

euler_problem: int = 537
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 3, 'k': 3}, 'answer': None},
    {'category': 'main', 'input': {'n': 20000, 'k': 20000}, 'answer': None},
]
encrypted: str = (
    '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'
    'g3C4MAZZenM='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
