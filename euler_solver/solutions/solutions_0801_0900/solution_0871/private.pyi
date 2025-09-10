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

Solution Approach:
    Model the problem in terms of graph theory and set theory; each f_n is a function on a finite
    set, interpret subsets and their images under f_n.
    Use combinatorics and possibly search or optimization techniques to find drifting subsets.
    Employ modular arithmetic properties for efficient computations.
    The complexity depends on how efficiently drifting subsets can be characterized or found.

Answer: ...
URL: https://projecteuler.net/problem=871
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 871
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}},
    {'category': 'main', 'input': {'max_limit': 100005}},
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_drifting_subsets_p0871_s0(*, max_limit: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))
