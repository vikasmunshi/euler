#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 871: Drifting Subsets.

Problem Statement:
    Let f be a function from a finite set S to itself. A drifting subset for f is a subset
    A of S such that the number of elements in the union A ∪ f(A) is equal to twice the
    number of elements of A.
    We write D(f) for the maximal number of elements among all drifting subsets for f.

    For a positive integer n, define f_n as the function from {0, 1, ..., n - 1} to itself sending
    x to x^3 + x + 1 mod n.
    You are given D(f_5) = 1 and D(f_10) = 3.

    Find the sum from i = 1 to 100 of D(f_(10^5 + i)).

URL: https://projecteuler.net/problem=871
"""
from typing import Any

euler_problem: int = 871
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 100005}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
