#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 872: Recursive Tree.

Problem Statement:
    A sequence of rooted trees T_n is constructed such that T_n has n nodes numbered
    1 to n.

    The sequence starts at T_1, a tree with a single node as a root with the number 1.

    For n > 1, T_n is constructed from T_{n-1} using the following procedure:

        1. Trace a path from the root of T_{n-1} to a leaf by following the largest-
           numbered child at each node.
        2. Remove all edges along the traced path, disconnecting all nodes along it
           from their parents.
        3. Connect all orphaned nodes directly to a new node numbered n, which becomes
           the root of T_n.

    For example, the following figure shows T_6 and T_7. The path traced through T_6
    during the construction of T_7 is coloured red.

    Let f(n, k) be the sum of the node numbers along the path connecting the root of
    T_n to the node k, including the root and the node k. For example, f(6, 1) = 6 + 5 + 1 = 12
    and f(10, 3) = 29.

    Find f(10^17, 9^17).

URL: https://projecteuler.net/problem=872
"""
from typing import Any

euler_problem: int = 872
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
