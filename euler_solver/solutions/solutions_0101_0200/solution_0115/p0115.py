#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 115: Counting Block Combinations II.

Problem Statement:
    A row measuring n units in length has red blocks with a minimum length of m
    units placed on it, such that any two red blocks (which are allowed to be
    different lengths) are separated by at least one black square.

    Let the fill-count function, F(m, n), represent the number of ways that a row
    can be filled.

    For example, F(3, 29) = 673135 and F(3, 30) = 1089155.

    That is, for m = 3, it can be seen that n = 30 is the smallest value for which
    the fill-count function first exceeds one million.

    In the same way, for m = 10, it can be verified that F(10, 56) = 880711 and
    F(10, 57) = 1148904, so n = 57 is the least value for which the fill-count
    function first exceeds one million.

    For m = 50, find the least value of n for which the fill-count function first
    exceeds one million.

URL: https://projecteuler.net/problem=115
"""
from typing import Any

euler_problem: int = 115
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'m': 3, 'limit': 1000000}, 'answer': None},
    {'category': 'dev', 'input': {'m': 10, 'limit': 1000000}, 'answer': None},
    {'category': 'main', 'input': {'m': 50, 'limit': 1000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
