#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 821: 123-Separable.

Problem Statement:
    A set, S, of integers is called 123-separable if S, 2S and 3S are disjoint. Here 2S and 3S
    are obtained by multiplying all the elements in S by 2 and 3 respectively.

    Define F(n) to be the maximum number of elements of
    (S union 2S union 3S) intersected with {1,2,3,...,n}
    where S ranges over all 123-separable sets.

    For example, F(6) = 5 can be achieved with either S = {1,4,5} or S = {1,5,6}.
    You are also given F(20) = 19.

    Find F(10^16).

URL: https://projecteuler.net/problem=821
"""
from typing import Any

euler_problem: int = 821
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 20}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 10000000000000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
