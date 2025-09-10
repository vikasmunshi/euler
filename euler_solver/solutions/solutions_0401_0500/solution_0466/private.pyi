#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 466: Distinct Terms in a Multiplication Table.

Problem Statement:
    Let P(m,n) be the number of distinct terms in an m times n multiplication table.

    For example, a 3 times 4 multiplication table looks like this:

        1    2    3    4
        2    4    6    8
        3    6    9   12

    There are 8 distinct terms {1,2,3,4,6,8,9,12}, therefore P(3,4) = 8.

    You are given that:
    P(64,64) = 1263,
    P(12,345) = 1998, and
    P(32,10^15) = 13826382602124302.

    Find P(64,10^16).

Solution Approach:
    This problem involves efficient counting of distinct products in large multiplication
    tables. Key ideas include number theory, fast enumeration of products, and possibly
    advanced factorization or counting methods. Handling huge limits requires highly
    optimized algorithms, possibly combining sieves, prime factorization insights,
    and fast summation techniques. Expected complexity is heavily dependent on the
    approach, aiming for sub-linear factors in large n.

Answer: ...
URL: https://projecteuler.net/problem=466
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 466
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'m': 64, 'n': 10**16}},
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_distinct_terms_in_a_multiplication_table_p0466_s0(*, m: int, n: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))