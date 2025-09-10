#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 46: Goldbach's Other Conjecture.

Problem Statement:
    It was proposed by Christian Goldbach that every odd composite number can be
    written as the sum of a prime and twice a square.

    9 = 7 + 2 x 1^2
    15 = 7 + 2 x 2^2
    21 = 3 + 2 x 3^2
    25 = 7 + 2 x 3^2
    27 = 19 + 2 x 2^2
    33 = 31 + 2 x 1^2

    It turns out that the conjecture was false.

    What is the smallest odd composite that cannot be written as the sum of a prime
    and twice a square?

Solution Approach:
    Use number theory and prime checking. Generate odd composites and verify if they
    can be expressed as prime + 2 * (square). Use efficient prime generation/check
    and iterate over squares. Expected complexity is moderate due to simple checks.

Answer: ...
URL: https://projecteuler.net/problem=46
"""
from __future__ import annotations

from typing import Any, Dict, List, Set

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 46
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_goldbachs_other_conjecture_p0046_s0() -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))
