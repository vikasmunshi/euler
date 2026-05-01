#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 473: Phigital Number Base.

Problem Statement:
    Let phi be the golden ratio: phi = (1 + sqrt(5)) / 2.
    Remarkably it is possible to write every positive integer as a sum of powers of phi
    even if we require that every power of phi is used at most once in this sum.
    Even then this representation is not unique.
    We can make it unique by requiring that no powers with consecutive exponents are used
    and that the representation is finite.
    E.g:
        2 = phi + phi^(-2)
        3 = phi^2 + phi^(-2)

    To represent this sum of powers of phi we use a string of 0's and 1's with a point to
    indicate where the negative exponents start.
    We call this the representation in the phigital number base.
    So 1 = 1_phi, 2 = 10.01_phi, 3 = 100.01_phi and 14 = 100100.001001_phi.
    The strings representing 1, 2 and 14 in the phigital number base are palindromic,
    while the string representing 3 is not.
    (the phigital point is not the middle character).

    The sum of the positive integers not exceeding 1000 whose phigital representation is
    palindromic is 4345.

    Find the sum of the positive integers not exceeding 10^10 whose phigital representation
    is palindromic.

URL: https://projecteuler.net/problem=473
"""
from typing import Any

euler_problem: int = 473
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 1000}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 10000000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
