#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 594: Rhombus Tilings.

Problem Statement:
    For a polygon P, let t(P) be the number of ways in which P can be tiled using rhombi
    and squares with edge length 1. Distinct rotations and reflections are counted as
    separate tilings.

    For example, if O is a regular octagon with edge length 1, then t(O) = 8. As it happens,
    all these 8 tilings are rotations of one another.

    Let O_a,b be the equal-angled convex octagon whose edges alternate in length between a
    and b. For example, here is O_2,1, with one of its tilings.

    You are given that t(O_1,1) = 8, t(O_2,1) = 76 and t(O_3,2) = 456572.

    Find t(O_4,2).

URL: https://projecteuler.net/problem=594
"""
from typing import Any

euler_problem: int = 594
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
