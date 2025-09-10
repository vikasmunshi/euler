#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 580: Squarefree Hilbert Numbers.

Problem Statement:
    A Hilbert number is any positive integer of the form 4k+1 for integer k ≥ 0.
    We shall define a squarefree Hilbert number as a Hilbert number which is not
    divisible by the square of any Hilbert number other than one.
    For example, 117 is a squarefree Hilbert number, equaling 9×13.
    However 6237 is a Hilbert number that is not squarefree in this sense,
    as it is divisible by 9^2.
    The number 3969 is also not squarefree, as it is divisible by both 9^2 and 21^2.

    There are 2327192 squarefree Hilbert numbers below 10^7.
    How many squarefree Hilbert numbers are there below 10^16?

Solution Approach:
    Use number theory and sieve methods specialized to Hilbert numbers.
    Identify Hilbert numbers and prime Hilbert numbers; apply inclusion-exclusion
    to count squarefree Hilbert numbers below 10^16.
    Efficiently sieve using properties of arithmetic progressions.
    Expected to be a challenging computational problem requiring optimized math.

Answer: ...
URL: https://projecteuler.net/problem=580
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 580
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10000000}},  # 10^7 known case
    {'category': 'main', 'input': {'max_limit': 10000000000000000}},  # 10^16 official problem
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_squarefree_hilbert_numbers_p0580_s0(*, max_limit: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))