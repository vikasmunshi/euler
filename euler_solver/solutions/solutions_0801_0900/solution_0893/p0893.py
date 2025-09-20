#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 893: Matchsticks.

Problem Statement:
    Define M(n) to be the minimum number of matchsticks needed to represent the number n.

    A number can be represented in digit form or as an expression involving addition and/or
    multiplication. Also order of operations must be followed, that is multiplication binding
    tighter than addition. Any other symbols or operations, such as brackets, subtraction,
    division or exponentiation, are not allowed.

    The valid digits and symbols are shown below:
    (A diagram depicts digits and symbols with their respective matchstick counts.)

    For example, 28 needs 12 matchsticks to represent it in digit form but representing it as
    4×7 would only need 9 matchsticks and as there is no way using fewer matchsticks
    M(28) = 9.

    Define T(N) = sum of M(n) for n = 1 to N. You are given T(100) = 916.

    Find T(10^6).

URL: https://projecteuler.net/problem=893
"""
from typing import Any

euler_problem: int = 893
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 100}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 1000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
