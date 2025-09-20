#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 874: Maximal Prime Score.

Problem Statement:
    Let p(t) denote the (t+1)th prime number. So that p(0) = 2, p(1) = 3, etc.
    We define the prime score of a list of nonnegative integers [a_1, ..., a_n]
    as the sum of p(a_i) for i from 1 to n.

    Let M(k, n) be the maximal prime score among all lists [a_1, ..., a_n] such that:
        0 <= a_i < k for each i;
        the sum of a_i is a multiple of k.

    For example, M(2, 5) = 14 as [0, 1, 1, 1, 1] attains a maximal prime score of 14.

    Find M(7000, p(7000)).

URL: https://projecteuler.net/problem=874
"""
from typing import Any

euler_problem: int = 874
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'k': 7000, 'n': 7000}, 'answer': None},
]
encrypted: str = (
    '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'
    '1diFO8xevfo='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
