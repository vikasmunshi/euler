#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 805: Shifted Multiples.

Problem Statement:
    For a positive integer n, let s(n) be the integer obtained by shifting the
    leftmost digit of the decimal representation of n to the rightmost position.
    For example, s(142857)=428571 and s(10)=1.

    For a positive rational number r, we define N(r) as the smallest positive
    integer n such that s(n)=r * n. If no such integer exists, then N(r) is zero.
    For example, N(3)=142857, N(1/10)=10, and N(2)=0.

    Let T(M) be the sum of N(u^3/v^3) where (u,v) ranges over all ordered pairs
    of coprime positive integers not exceeding M.
    For example, T(3) ≡ 262429173 (mod 1000000007).

    Find T(200). Give your answer modulo 1000000007.

URL: https://projecteuler.net/problem=805
"""
from typing import Any

euler_problem: int = 805
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'max_limit': 200}, 'answer': None},
]
encrypted: str = (
    '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'
    'ByHvZqLH+RlXABrCL/8Cfg=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
