#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 778: Freshman's Product.

Problem Statement:
    If a,b are two nonnegative integers with decimal representations a=(... a_2a_1a_0)
    and b=(... b_2b_1b_0) respectively, then the freshman's product of a and b, denoted
    a⊠b, is the integer c with decimal representation c=(... c_2c_1c_0) such that c_i is
    the last digit of a_i·b_i.

    For example, 234⊠765 = 480.

    Let F(R,M) be the sum of x_1⊠...⊠x_R for all sequences of integers (x_1,...,x_R)
    with 0 ≤ x_i ≤ M.

    For example, F(2, 7) = 204, and F(23, 76) ≡ 5870548 (mod 1 000 000 009).

    Find F(234567, 765432), give your answer modulo 1 000 000 009.

Solution Approach:
    Use combinatorics and modular arithmetic. Represent numbers digit-wise and leverage
    independence of each digit product modulo 10. Use dynamic programming or fast exponentiation
    of digit distributions. Expected complexity managed by digit-wise separation and modular sums.

Answer: ...
URL: https://projecteuler.net/problem=778
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 778
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'R': 2, 'M': 7}},
    {'category': 'main', 'input': {'R': 234567, 'M': 765432}},
    {'category': 'extra', 'input': {'R': 1000000, 'M': 1000000}},
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_freshmans_product_p0778_s0(*, R: int, M: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))