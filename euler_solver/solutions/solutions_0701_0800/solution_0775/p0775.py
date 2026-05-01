#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 775: Saving Paper.

Problem Statement:
    When wrapping several cubes in paper, it is more efficient to wrap them all
    together than to wrap each one individually. For example, with 10 cubes of
    unit edge length, it would take 30 units of paper to wrap them in the
    arrangement shown below, but 60 units to wrap them separately.

    Define g(n) to be the maximum amount of paper that can be saved by wrapping
    n identical 1 x 1 x 1 cubes in a compact arrangement, compared with wrapping
    them individually. We insist that the wrapping paper is in contact with the
    cubes at all points, without leaving a void.

    With 10 cubes, the arrangement illustrated above is optimal, so g(10) = 60 - 30 = 30.
    With 18 cubes, it can be shown that the optimal arrangement is as a 3 x 3 x 2,
    using 42 units of paper, whereas wrapping individually would use 108 units of
    paper; hence g(18) = 66.

    Define
        G(N) = sum_{n=1}^N g(n)

    You are given that G(18) = 530, and G(10^6) ≡ 951640919 (mod 1,000,000,007).

    Find G(10^{16}). Give your answer modulo 1,000,000,007.

URL: https://projecteuler.net/problem=775
"""
from typing import Any

euler_problem: int = 775
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 10000000000000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
