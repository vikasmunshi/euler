#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 880: Nested Radicals.

Problem Statement:
    (x,y) is called a nested radical pair if x and y are non-zero integers such that
    x/y is not a cube of a rational number, and there exist integers a, b and c such
    that:

        sqrt(cube_root(x) + cube_root(y)) = cube_root(a) + cube_root(b) + cube_root(c).

    For example, both (-4,125) and (5,5324) are nested radical pairs:

        sqrt(cube_root(-4) + cube_root(125)) = cube_root(-1) + cube_root(2) + cube_root(4)
        sqrt(cube_root(5) + cube_root(5324)) = cube_root(-2) + cube_root(20) + cube_root(25).

    Let H(N) be the sum of |x|+|y| for all the nested radical pairs (x, y) where
    |x| <= |y| <= N.
    For example, H(10^3) = 2535.

    Find H(10^15). Give your answer modulo 1031^3 + 2.

URL: https://projecteuler.net/problem=880
"""
from typing import Any

euler_problem: int = 880
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 1000}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 1000000000000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'dSmmuzPcx/6Q5WBRSFTT7g=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
