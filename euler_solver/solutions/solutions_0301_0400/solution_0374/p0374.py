#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 374: Maximum Integer Partition Product.

Problem Statement:
    An integer partition of a number n is a way of writing n as a sum of positive
    integers.
    Partitions that differ only in the order of their summands are considered the
    same. A partition of n into distinct parts is a partition of n in which every
    part occurs at most once.
    The partitions of 5 into distinct parts are:
    5, 4+1 and 3+2.
    Let f(n) be the maximum product of the parts of any such partition of n into
    distinct parts and let m(n) be the number of elements of any such partition
    of n with that product.
    So f(5) = 6 and m(5) = 2.
    For n = 10 the partition with the largest product is 10 = 2+3+5, which gives
    f(10) = 30 and m(10) = 3. Their product f(10) * m(10) = 30 * 3 = 90.
    It can be verified that sum f(n) * m(n) for 1 <= n <= 100 = 1683550844462.
    Find sum f(n) * m(n) for 1 <= n <= 10^14.
    Give your answer modulo 982451653, the 50 millionth prime.

URL: https://projecteuler.net/problem=374
"""
from typing import Any

euler_problem: int = 374
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 100}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 100000000000000}, 'answer': None},
    {'category': 'extra', 'input': {'max_limit': 1000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'RhDcgb2rWmplP6ucu5osVxvPc4VXSg+V1WVBTg=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
