#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 789: Minimal Pairing Modulo p.

Problem Statement:
    Given an odd prime p, put the numbers 1,...,p-1 into (p-1)/2 pairs such that each
    number appears exactly once. Each pair (a,b) has a cost of ab mod p. For example,
    if p=5 the pair (3,4) has a cost of 12 mod 5 = 2.

    The total cost of a pairing is the sum of the costs of its pairs. We say that such
    pairing is optimal if its total cost is minimal for that p.

    For example, if p = 5, then there is a unique optimal pairing: (1, 2), (3, 4),
    with total cost of 2 + 2 = 4.

    The cost product of a pairing is the product of the costs of its pairs. For example,
    the cost product of the optimal pairing for p = 5 is 2 * 2 = 4.

    It turns out that all optimal pairings for p = 2,000,000,011 have the same cost
    product.

    Find the value of this product.

URL: https://projecteuler.net/problem=789
"""
from typing import Any

euler_problem: int = 789
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'p': 2000000011}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
