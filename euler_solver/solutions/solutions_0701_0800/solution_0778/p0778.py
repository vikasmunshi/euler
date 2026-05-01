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

URL: https://projecteuler.net/problem=778
"""
from typing import Any

euler_problem: int = 778
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'R': 2, 'M': 7}, 'answer': None},
    {'category': 'main', 'input': {'R': 234567, 'M': 765432}, 'answer': None},
    {'category': 'extra', 'input': {'R': 1000000, 'M': 1000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'ZDjtoQ=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
