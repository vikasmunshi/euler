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

Solution Approach:
    Use number theory and analysis on prime factorization distributions.
    Evaluate expected values over integers considering the distribution of prime factors
    and their p-adic orders.
    Possibly employ analytic number theory or probabilistic models.
    Summation over infinite series requires convergence proof or closed form.
    Expected complexity depends on numerical approximation or closed-form derivation.

Answer: ...
URL: https://projecteuler.net/problem=779
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 779
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}},
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_prime_factor_and_exponent_p0779_s0() -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))