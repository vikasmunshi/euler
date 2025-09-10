#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 866: Tidying Up B.

Problem Statement:
    A small child has a “number caterpillar” consisting of N jigsaw pieces,
    each with one number on it, which, when connected together in a line,
    reveal the numbers 1 to N in order.

    Every night, the child's father has to pick up the pieces of the caterpillar
    that have been scattered across the play room. He picks up the pieces at
    random and places them in the correct order.
    As the caterpillar is built up in this way, it forms distinct segments that
    gradually merge together.

    Any time the father places a new piece in its correct position, a segment
    of length k is formed and he writes down the k-th hexagonal number
    k*(2k-1). Once all pieces have been placed and the full caterpillar
    constructed he calculates the product of all the numbers written down.
    Interestingly, the expected value of this product is always an integer.
    For example if N=4 then the expected value is 994.

    Find the expected value of the product for a caterpillar of N=100 pieces.
    Give your answer modulo 987654319.

Solution Approach:
    Model the process of forming segments as a random permutation construction.
    Use combinatorics and expected values properties.
    Employ dynamic programming or memoization to efficiently compute expected
    products considering segment merges.
    Fast modular arithmetic is essential due to the large modulus.
    The approach should optimize over segment lengths and their formation
    probabilities to achieve feasible time complexity.

Answer: ...
URL: https://projecteuler.net/problem=866
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 866
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'n': 100}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_tidying_up_b_p0866_s0(*, n: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))