#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 791: Average and Variance.

Problem Statement:
    Denote the average of k numbers x1, ..., xk by x̄ = (1/k) sum_i x_i. Their variance
    is defined as (1/k) sum_i (x_i - x̄)^2.

    Let S(n) be the sum of all quadruples of integers (a,b,c,d) satisfying 1 <= a <= b <= c <= d <= n
    such that their average is exactly twice their variance.

    For n=5, there are 5 such quadruples, namely: (1,1,1,3), (1,1,3,3), (1,2,3,4), (1,3,4,4),
    (2,2,3,5).

    Hence S(5)=48. You are also given S(10^3)=37048340.

    Find S(10^8). Give your answer modulo 433494437.

URL: https://projecteuler.net/problem=791
"""
from typing import Any

euler_problem: int = 791
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 5}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 100000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'IPjtKkXdEHtS6/cc70SpTNNvnlT87qnWO3/p3Q=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
