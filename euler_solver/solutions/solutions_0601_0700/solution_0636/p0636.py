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

URL: https://projecteuler.net/problem=636
"""
from typing import Any

euler_problem: int = 636
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n_factorial': 25}, 'answer': None},
    {'category': 'main', 'input': {'n_factorial': 1000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
