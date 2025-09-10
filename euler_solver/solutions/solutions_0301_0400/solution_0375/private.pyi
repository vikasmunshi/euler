#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 375: Minimum of Subsequences.

Problem Statement:
    Let S_n be an integer sequence produced with the following pseudo-random
    number generator:
        S_0 = 290797
        S_{n+1} = S_n^2 mod 50515093

    Let A(i, j) be the minimum of the numbers S_i, S_{i+1}, ..., S_j for
    i ≤ j.
    Let M(N) = sum A(i, j) for 1 ≤ i ≤ j ≤ N.
    We can verify that M(10) = 432256955 and M(10000) = 3264567774119.

    Find M(2000000000).

Solution Approach:
    Generate the sequence S_n using the given quadratic congruential rule; note
    the sequence eventually repeats because values are modulo 50515093.
    Reduce the problem to summing subarray minima: for a finite array the sum
    of all subarray minima can be computed by, for each element, finding the
    span where it is the minimum (using monotonic stacks) and accumulating its
    contribution as value * left_count * right_count.
    For N much larger than the RNG period, detect the transient and cycle and
    aggregate contributions over full cycles plus a prefix remainder.
    Complexity: O(m) to preprocess distinct sequence values (m ≤ modulus) and
    O(1) per distinct element for contribution aggregation; space O(m).

Answer: ...
URL: https://projecteuler.net/problem=375
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 375
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 10}},
    {'category': 'main', 'input': {'n': 2000000000}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_minimum_of_subsequences_p0375_s0(*, n: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))