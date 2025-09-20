#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 619: Square Subsets.

Problem Statement:
    For a set of positive integers {a, a+1, a+2, ..., b}, let C(a,b) be the number of
    non-empty subsets in which the product of all elements is a perfect square.

    For example C(5,10)=3, since the products of all elements of {5, 8, 10}, {5, 8, 9, 10}
    and {9} are perfect squares, and no other subsets of {5, 6, 7, 8, 9, 10} have this property.

    You are given that C(40,55) = 15, and C(1000,1234) mod 1000000007 = 975523611.

    Find C(1000000,1234567) mod 1000000007.

URL: https://projecteuler.net/problem=619
"""
from typing import Any

euler_problem: int = 619
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'a': 5, 'b': 10}, 'answer': None},
    {'category': 'main', 'input': {'a': 1000000, 'b': 1234567}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
