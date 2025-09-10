#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 773: Ruff Numbers.

Problem Statement:
    Let S_k be the set containing 2 and 5 and the first k primes that end in 7.
    For example, S_3 = {2, 5, 7, 17, 37}.

    Define a k-Ruff number to be one that is not divisible by any element in S_k.

    If N_k is the product of the numbers in S_k then define F(k) to be the sum of all
    k-Ruff numbers less than N_k that have last digit 7. You are given F(3) = 76101452.

    Find F(97), give your answer modulo 1000000007.

Solution Approach:
    Use number theory and combinatorics. Build the set S_k with primes ending in 7 plus 2 and 5.
    Compute N_k as the product of elements in S_k.
    Use the principle of inclusion–exclusion to find k-Ruff numbers ending with digit 7
    under N_k efficiently. Modular arithmetic is needed for the sum modulo 1,000,000,007.
    Time complexity depends on inclusion–exclusion optimization due to large k=97.

Answer: ...
URL: https://projecteuler.net/problem=773
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 773
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'k': 3}},
    {'category': 'main', 'input': {'k': 97}},
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_ruff_numbers_p0773_s0(*, k: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))