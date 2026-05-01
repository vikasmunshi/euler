#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 927: Prime-ary Tree.

Problem Statement:
    A full k-ary tree is a tree with a single root node, such that every node is
    either a leaf or has exactly k ordered children. The height of a k-ary tree is
    the number of edges in the longest path from the root to a leaf.

    For instance, there is one full 3-ary tree of height 0, one full 3-ary tree of
    height 1, and seven full 3-ary trees of height 2. These seven are shown below.

    For integers n and k with n >= 0 and k >= 2, define t_k(n) to be the number of
    full k-ary trees of height n or less. Thus, t_3(0) = 1, t_3(1) = 2, and t_3(2) = 9.
    Also, t_2(0) = 1, t_2(1) = 2, and t_2(2) = 5.

    Define S_k to be the set of positive integers m such that m divides t_k(n) for
    some integer n >= 0. For instance, the above values show that 1, 2, and 5 are
    in S_2 and 1, 2, 3, and 9 are in S_3.

    Let S be the intersection over all primes p of the sets S_p, that is S = intersection_p S_p.
    Finally, define R(N) to be the sum of all elements of S not exceeding N. You are
    given that R(20) = 18 and R(1000) = 2089.

    Find R(10^7).

URL: https://projecteuler.net/problem=927
"""
from typing import Any

euler_problem: int = 927
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 20}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 10000000}, 'answer': None},
    {'category': 'extra', 'input': {'max_limit': 1000}, 'answer': None},
]
encrypted: str = (
    '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'
    'JjdFXnZ+Vh7x1FNTP6SO3fK2etk='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
