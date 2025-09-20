#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 558: Irrational Base.

Problem Statement:
    Let r be the real root of the equation x^3 = x^2 + 1.
    Every positive integer can be written as the sum of distinct increasing powers of r.
    If we require the number of terms to be finite and the difference between any two
    exponents to be three or more, then the representation is unique.
    For example, 3 = r^-10 + r^-5 + r^-1 + r^2 and 10 = r^-10 + r^-7 + r^6.
    Interestingly, the relation holds for the complex roots of the equation.

    Let w(n) be the number of terms in this unique representation of n. Thus w(3) = 4
    and w(10) = 3.

    More formally, for all positive integers n, we have:
    n = sum over k from -∞ to ∞ of b_k * r^k
    under the conditions that:
    b_k is 0 or 1 for all k;
    b_k + b_(k+1) + b_(k+2) <= 1 for all k;
    w(n) = sum over k from -∞ to ∞ of b_k is finite.

    Let S(m) = sum from j=1 to m of w(j^2).
    You are given S(10) = 61 and S(1000) = 19403.

    Find S(5,000,000).

URL: https://projecteuler.net/problem=558
"""
from typing import Any

euler_problem: int = 558
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 5000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'tVcML3wZCYoCkRwyFwR2sQQIJK4mu1fgSWxwdw=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
