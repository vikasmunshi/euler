#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 892: Zebra Circles.

Problem Statement:
    Consider a circle where 2n distinct points have been marked on its circumference.

    A cutting C consists of connecting the 2n points with n line segments, so that no two
    line segments intersect, including on their end points. The n line segments then cut
    the circle into n + 1 pieces.
    Each piece is painted either black or white, so that adjacent pieces are opposite colours.
    Let d(C) be the absolute difference between the numbers of black and white pieces under
    the cutting C.

    Let D(n) be the sum of d(C) over all different cuttings C.
    For example, there are five different cuttings with n = 3.

    The upper three cuttings all have d = 0 because there are two black and two white pieces;
    the lower two cuttings both have d = 2 because there are three black and one white pieces.
    Therefore D(3) = 0 + 0 + 0 + 2 + 2 = 4.
    You are also given D(100) ≡ 1172122931 (mod 1234567891).

    Find the sum from n=1 to 10^7 of D(n). Give your answer modulo 1234567891.

URL: https://projecteuler.net/problem=892
"""
from typing import Any

euler_problem: int = 892
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 10000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'KABWysYe1mXWzrfVZt6TXUxvLgJHAwFdV+LyqQ=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
