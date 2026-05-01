#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 829: Integral Fusion.

Problem Statement:
    Given any integer n > 1 a binary factor tree T(n) is defined to be:
    - A tree with the single node n when n is prime.
    - A binary tree that has root node n, left subtree T(a) and right subtree T(b),
      when n is not prime. Here a and b are positive integers such that n = ab,
      a ≤ b and b - a is the smallest.

    For example T(20):

    We define M(n) to be the smallest number that has a factor tree identical in shape
    to the factor tree for n!!, the double factorial of n.

    For example, consider 9!! = 9×7×5×3×1 = 945. The factor tree for 945 is shown
    together with the factor tree for 72 which is the smallest number that has a
    factor tree of the same shape. Hence M(9) = 72.

    Find the sum from n=2 to 31 of M(n).

URL: https://projecteuler.net/problem=829
"""
from typing import Any

euler_problem: int = 829
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
