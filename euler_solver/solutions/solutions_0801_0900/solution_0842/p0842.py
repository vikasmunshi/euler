#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 842: Irregular Star Polygons.

Problem Statement:
    Given n equally spaced points on a circle, we define an n-star polygon as an
    n-gon having those n points as vertices. Two n-star polygons differing by a
    rotation or reflection are considered different.

    For example, there are twelve 5-star polygons.

    For an n-star polygon S, let I(S) be the number of its self intersection points.
    Let T(n) be the sum of I(S) over all n-star polygons S.
    For the example above T(5) = 20 because in total there are 20 self intersection points.

    Some star polygons may have intersection points made from more than two lines.
    These are only counted once. For example, S shown below is one of the sixty 6-star polygons.
    This one has I(S) = 4.

    You are also given that T(8) = 14640.

    Find the sum from n=3 to n=60 of T(n). Give your answer modulo (10^9 + 7).

URL: https://projecteuler.net/problem=842
"""
from typing import Any

euler_problem: int = 842
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}, 'answer': None},
]
encrypted: str = (
    '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'
    'HFPuHBqGxG8='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
