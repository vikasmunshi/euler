#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 854: Pisano Periods 2.

Problem Statement:
    For every positive integer n the Fibonacci sequence modulo n is periodic. The period
    depends on the value of n. This period is called the Pisano period for n, often
    shortened to π(n).

    Define M(p) as the largest integer n such that π(n) = p, and define M(p) = 1 if there is
    no such n. For example, there are three values of n for which π(n) equals 18: 19, 38,
    76. Therefore M(18) = 76.

    Let the product function P(n) be:
        P(n) = ∏_{p=1}^{n} M(p).

    You are given: P(10) = 264.

    Find P(1,000,000) modulo 1,234,567,891.

Solution Approach:
    Key ideas include number theory focusing on Pisano periods and their properties.
    The problem involves computing maximal n for given Pisano periods p, then
    product accumulation modulo a large modulus. Efficient computation may require
    factorization, multiplicative order considerations, and fast algorithms for
    Pisano periods. Time complexity depends on implementing these number-theoretic
    functions efficiently and managing large products modulo the given modulus.

Answer: ...
URL: https://projecteuler.net/problem=854
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 854
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_p': 10}},
    {'category': 'main', 'input': {'max_p': 1000000}},
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_pisano_periods_2_p0854_s0(*, max_p: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))