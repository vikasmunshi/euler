#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 926: Total Roundness.

Problem Statement:
    A round number is a number that ends with one or more zeros in a given base.

    Let us define the roundness of a number n in base b as the number of zeros at the
    end of the base b representation of n.
    For example, 20 has roundness 2 in base 2, because the base 2 representation of 20
    is 10100, which ends with 2 zeros.

    Also define R(n), the total roundness of a number n, as the sum of the roundness of
    n in base b for all b > 1.
    For example, 20 has roundness 2 in base 2 and roundness 1 in base 4, 5, 10, 20,
    hence we get R(20)=6.
    You are also given R(10!) = 312.

    Find R(10000000!). Give your answer modulo 10^9 + 7.

Solution Approach:
    Use number theory and factorization properties of factorial numbers.
    The problem involves counting trailing zeroes in all bases > 1, which relates to
    prime factorization and valuations.
    Efficient prime factorization and summation with modulo arithmetic will be key.
    The solution should handle large factorial inputs and use math identities and
    combinatorics for performance.

Answer: ...
URL: https://projecteuler.net/problem=926
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 926
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 10}},
    {'category': 'main', 'input': {'n': 10000000}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_total_roundness_p0926_s0(*, n: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))