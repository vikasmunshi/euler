#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 648: Skipping Squares.

Problem Statement:
    For some fixed ρ in [0, 1], we begin a sum s at 0 and repeatedly apply a process:
    With probability ρ, we add 1 to s, otherwise we add 2 to s.

    The process ends when either s is a perfect square or s exceeds 10^18, whichever occurs
    first. For example, if s goes through 0, 2, 3, 5, 7, 9, the process ends at s=9, and two
    squares 1 and 4 were skipped over.

    Let f(ρ) be the expected number of perfect squares skipped over when the process finishes.

    It can be shown that the power series for f(ρ) is sum from k=0 to ∞ of a_k ρ^k for a suitable
    (unique) choice of coefficients a_k. Some of the first few coefficients are a_0=1, a_1=0,
    a_5=-18, a_10=45176.

    Let F(n) = sum from k=0 to n of a_k. You are given that F(10) = 53964 and F(50) ≡ 842418857
    (mod 10^9).

    Find F(1000), and give your answer modulo 10^9.

URL: https://projecteuler.net/problem=648
"""
from typing import Any

euler_problem: int = 648
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}, 'answer': None},
]
encrypted: str = (
    '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'
    'ln55hXdM3U4='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
