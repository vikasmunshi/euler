#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 226: A Scoop of Blancmange.

Problem Statement:
    The blancmange curve is the set of points (x, y) such that 0 <= x <= 1
    and y = sum_{n=0}^infty s(2^n x)/2^n, where s(x) is the distance from x to
    the nearest integer.

    The area under the blancmange curve is equal to 1/2, shown in pink in the
    diagram.

    Let C be the circle with centre (1/4, 1/2) and radius 1/4, shown in black.

    What area under the blancmange curve is enclosed by C?
    Give your answer rounded to eight decimal places in the form 0.abcdefgh.

URL: https://projecteuler.net/problem=226
"""
from typing import Any

euler_problem: int = 226
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
