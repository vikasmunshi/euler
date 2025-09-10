#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 636: Restricted Factorisations.

Problem Statement:
    Consider writing a natural number as product of powers of natural numbers
    with given exponents, additionally requiring different base numbers for each
    power.

    For example, 256 can be written as a product of a square and a fourth power
    in three ways such that the base numbers are different.
    That is, 256=1^2×4^4=4^2×2^4=16^2×1^4

    Though 4^2 and 2^4 are both equal, we are concerned only about the base
    numbers in this problem. Note that permutations are not considered distinct,
    for example 16^2×1^4 and 1^4×16^2 are considered to be the same.

    Similarly, 10! can be written as a product of one natural number, two squares
    and three cubes in two ways (10!=42×5^2×4^2×3^3×2^3×1^3=21×5^2×2^2×4^3×3^3×1^3)
    whereas 20! can be given the same representation in 41680 ways.

    Let F(n) denote the number of ways in which n can be written as a product of
    one natural number, two squares, three cubes and four fourth powers.

    You are given that F(25!)=4933, F(100!) mod 1,000,000,007=693,952,493,
    and F(1,000!) mod 1,000,000,007=6,364,496.

    Find F(1,000,000!) mod 1,000,000,007.

Solution Approach:
    Use prime factorization and combinatorial number theory to count factorizations
    respecting powers and distinct bases. Handle factorial prime exponents via
    Legendre's formula. Employ multi-dimensional dynamic programming or combinatorics
    to combine counts. Modulo arithmetic is needed due to large results.

Answer: ...
URL: https://projecteuler.net/problem=636
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 636
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n_factorial': 25}},
    {'category': 'main', 'input': {'n_factorial': 1000000}},
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_restricted_factorisations_p0636_s0(*, n_factorial: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))