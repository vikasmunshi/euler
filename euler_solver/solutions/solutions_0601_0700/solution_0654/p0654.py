#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 654: Neighbourly Constraints.

Problem Statement:
    Let T(n, m) be the number of m-tuples of positive integers such that the sum
    of any two neighbouring elements of the tuple is ≤ n.

    For example, T(3, 4)=8, via the following eight 4-tuples:
    (1, 1, 1, 1)
    (1, 1, 1, 2)
    (1, 1, 2, 1)
    (1, 2, 1, 1)
    (1, 2, 1, 2)
    (2, 1, 1, 1)
    (2, 1, 1, 2)
    (2, 1, 2, 1)

    You are also given that T(5, 5)=246, T(10, 10^2) ≡ 862820094 mod 1000000007,
    and T(10^2, 10) ≡ 782136797 mod 1000000007.

    Find T(5000, 10^12) mod 1000000007.

URL: https://projecteuler.net/problem=654
"""
from typing import Any

euler_problem: int = 654
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 3, 'm': 4}, 'answer': None},
    {'category': 'main', 'input': {'n': 5000, 'm': 1000000000000}, 'answer': None},
    {'category': 'extra', 'input': {'n': 10000, 'm': 1000000000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'HxUbfI2aLX5MtOEHEUiT5pYrwYg='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
