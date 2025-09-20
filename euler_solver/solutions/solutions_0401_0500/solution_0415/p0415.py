#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 415: Titanic Sets.

Problem Statement:
    A set of lattice points S is called a titanic set if there exists a line
    passing through exactly two points in S.

    An example of a titanic set is S = {(0, 0), (0, 1), (0, 2), (1, 1), (2, 0), (1, 0)},
    where the line passing through (0, 1) and (2, 0) does not pass through any other
    point in S.

    On the other hand, the set {(0, 0), (1, 1), (2, 2), (4, 4)} is not a titanic set
    since the line passing through any two points in the set also passes through
    the other two.

    For any positive integer N, let T(N) be the number of titanic sets S whose every
    point (x, y) satisfies 0 <= x, y <= N.
    It can be verified that T(1) = 11, T(2) = 494, T(4) = 33554178,
    T(111) mod 10^8 = 13500401 and T(10^5) mod 10^8 = 63259062.

    Find T(10^11) mod 10^8.

URL: https://projecteuler.net/problem=415
"""
from typing import Any

euler_problem: int = 415
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 2}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 100000000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
