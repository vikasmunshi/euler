#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 779: Prime Factor and Exponent.

Problem Statement:
    For a positive integer n > 1, let p(n) be the smallest prime dividing n, and let
    alpha(n) be its p-adic order, i.e. the largest integer such that p(n)^alpha(n)
    divides n.

    For a positive integer K, define the function f_K(n) by:
        f_K(n) = (alpha(n) - 1) / (p(n))^K.

    Also define f̅_K by:
        f̅_K = lim_{N -> infinity} (1/N) * sum_{n=2}^N f_K(n).

    It can be verified that f̅_1 ≈ 0.282419756159.

    Find sum_{K=1}^∞ f̅_K. Give your answer rounded to 12 digits after the decimal point.

URL: https://projecteuler.net/problem=779
"""
from typing import Any

euler_problem: int = 779
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}, 'answer': None},
]
encrypted: str = (
    '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'
    'E4sFKYFu5F6dT9ihcnB+Aswi41wNI649g469+g=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
