#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 865: Triplicate Numbers.

Problem Statement:
    A triplicate number is a positive integer such that, after repeatedly removing
    three consecutive identical digits from it, all its digits can be removed.

    For example, the integer 122555211 is a triplicate number:
    122555211 -> 122(555)211 -> 1(222)11 -> (111) -> .

    On the other hand, neither 663633 nor 9990 are triplicate numbers.

    Let T(n) be how many triplicate numbers are less than 10^n.

    For example, T(6) = 261 and T(30) = 5576195181577716.

    Find T(10^4). Give your answer modulo 998244353.

URL: https://projecteuler.net/problem=865
"""
from typing import Any

euler_problem: int = 865
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'n': 10000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
