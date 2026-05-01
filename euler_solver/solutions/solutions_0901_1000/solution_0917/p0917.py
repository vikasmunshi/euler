#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 917: Minimal Path Using Additive Cost.

Problem Statement:
    The sequence s_n is defined by s_1 = 102022661 and s_n = s_(n-1)^2 mod 998388889
    for n > 1.

    Let a_n = s_(2n - 1) and b_n = s_(2n) for n=1,2,...

    Define an N x N matrix whose values are M_(i,j) = a_i + b_j.

    Let A(N) be the minimal path sum from M_(1,1) (top left) to M_(N,N) (bottom right),
    where each step is either right or down.

    You are given A(1) = 966774091, A(2) = 2388327490 and A(10) = 13389278727.

    Find A(10^7).

URL: https://projecteuler.net/problem=917
"""
from typing import Any

euler_problem: int = 917
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 2}, 'answer': None},
    {'category': 'main', 'input': {'n': 10000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
