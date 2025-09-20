#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 614: Special Partitions 2.

Problem Statement:
    An integer partition of a number n is a way of writing n as a sum of positive
    integers. Partitions that differ only by the order of their summands are
    considered the same.

    We call an integer partition special if 1) all its summands are distinct, and
    2) all its even summands are also divisible by 4.
    For example, the special partitions of 10 are:
        10 = 1+4+5 = 3+7 = 1+9
    The number 10 admits many more integer partitions (a total of 42), but only
    those three are special.

    Let P(n) be the number of special integer partitions of n. You are given that
    P(1) = 1, P(2) = 0, P(3) = 1, P(6) = 1, P(10) = 3, P(100) = 37076 and
    P(1000) = 3699177285485660336.

    Find the sum from i = 1 to 10^7 of P(i). Give the result modulo 10^9+7.

URL: https://projecteuler.net/problem=614
"""
from typing import Any

euler_problem: int = 614
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
