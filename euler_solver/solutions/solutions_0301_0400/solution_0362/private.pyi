#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 362: Squarefree Factors.

Problem Statement:
    Consider the number 54.
    54 can be factored in 7 distinct ways into one or more factors larger than 1:
    54, 2 x 27, 3 x 18, 6 x 9, 3 x 3 x 6, 2 x 3 x 9 and 2 x 3 x 3 x 3.
    If we require that the factors are all squarefree only two ways remain:
    3 x 3 x 6 and 2 x 3 x 3 x 3.

    Let's call Fsf(n) the number of ways n can be factored into one or more
    squarefree factors larger than 1, so Fsf(54)=2.

    Let S(n) be sum Fsf(k) for k = 2 to n.

    S(100)=193.

    Find S(10000000000).

Solution Approach:
    Treat Fsf as a multiplicative counting function derived from prime power
    contributions. Use number theory: factor n, analyze exponent partitions
    into squarefree factors, and exploit multiplicativity to form a Dirichlet
    convolution or generating function. Precompute contributions up to a
    bound using sieving/primes and combine via multiplicative formula.
    Aim for roughly sublinear behavior in n using prime sieves and divisor
    convolution. Expected complexity: roughly O(n^{2/3}) or better with
    advanced multiplicative summation techniques and memory O(n^{1/2}).

Answer: ...
URL: https://projecteuler.net/problem=362
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 362
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 100}},
    {'category': 'main', 'input': {'max_limit': 10000000000}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_squarefree_factors_p0362_s0(*, max_limit: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))