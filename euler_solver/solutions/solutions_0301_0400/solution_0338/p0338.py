#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 338: Cutting Rectangular Grid Paper.

Problem Statement:
    A rectangular sheet of grid paper with integer dimensions w x h is given. Its
    grid spacing is 1. When we cut the sheet along the grid lines into two pieces
    and rearrange those pieces without overlap, we can make new rectangles with
    different dimensions.

    For example, from a sheet with dimensions 9 x 4, we can make rectangles with
    dimensions 18 x 2, 12 x 3 and 6 x 6 by cutting and rearranging.

    Similarly, from a sheet with dimensions 9 x 8, we can make rectangles with
    dimensions 18 x 4 and 12 x 6.

    For a pair w and h, let F(w, h) be the number of distinct rectangles that can
    be made from a sheet with dimensions w x h. Examples: F(2,1) = 0,
    F(2,2) = 1, F(9,4) = 3 and F(9,8) = 2. Rectangles congruent to the initial
    one are not counted. Rectangles with dimensions w x h and h x w are not
    considered distinct.

    For an integer N, let G(N) be the sum of F(w, h) for all pairs w and h which
    satisfy 0 < h <= w <= N. We can verify that G(10) = 55, G(10^3) = 971745 and
    G(10^5) = 9992617687.

    Find G(10^12). Give your answer modulo 10^8.

URL: https://projecteuler.net/problem=338
"""
from typing import Any

euler_problem: int = 338
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 1000000000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'k5Qr7ihgKmM='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
