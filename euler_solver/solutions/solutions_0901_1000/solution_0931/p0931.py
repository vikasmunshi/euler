#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 931: Totient Graph.

Problem Statement:
    For a positive integer n construct a graph using all the divisors of n as the
    vertices. An edge is drawn between a and b if a is divisible by b and a/b is
    prime, and is given weight phi(a) - phi(b), where phi is the Euler totient function.
    Define t(n) to be the total weight of this graph.
    The example below shows that t(45) = 52

    Let T(N) = sum from n=1 to N of t(n). You are given T(10) = 26 and T(10^2) = 5282.

    Find T(10^12). Give your answer modulo 715827883.

URL: https://projecteuler.net/problem=931
"""
from typing import Any

euler_problem: int = 931
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 1000000000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
