#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 355: Maximal Coprime Subset.

Problem Statement:
    Define Co(n) to be the maximal possible sum of a set of mutually
    co-prime elements from {1,2,...,n}. For example Co(10) is 30 and hits
    that maximum on the subset {1,5,7,8,9}.

    You are given that Co(30) = 193 and Co(100) = 1356.

    Find Co(200000).

Solution Approach:
    Model this as a maximum-weight independent set on the conflict graph:
    nodes are 1..n and edges connect numbers with gcd>1. Exploit number
    theory to compress the graph by prime factors: numbers containing a
    large prime factor > n/2 are uniquely representable and can be treated
    greedily, while only small primes induce complex conflicts.
    Use DP or branch-and-bound over combinations of small primes with
    aggressive pruning and include numbers with unique prime factors greedily.
    Expected complexity is exponential in the count of small primes but
    manageable for n=200000 with suitable optimizations.

Answer: ...
URL: https://projecteuler.net/problem=355
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 355
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}},
    {'category': 'main', 'input': {'max_limit': 200000}},
    {'category': 'extra', 'input': {'max_limit': 1000000}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_maximal_coprime_subset_p0355_s0(*, max_limit: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))