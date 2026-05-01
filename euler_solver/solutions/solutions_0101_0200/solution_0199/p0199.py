#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 199: Iterative Circle Packing.

Problem Statement:
    Three circles of equal radius are placed inside a larger circle such that each
    pair of circles is tangent to one another and the inner circles do not overlap.
    There are four uncovered gaps which are to be filled iteratively with more
    tangent circles.

    At each iteration, a maximally sized circle is placed in each gap, which
    creates more gaps for the next iteration. After 3 iterations (pictured), there
    are 108 gaps and the fraction of the area which is not covered by circles is
    0.06790342, rounded to eight decimal places.

    What fraction of the area is not covered by circles after 10 iterations?
    Give your answer rounded to eight decimal places using the format x.xxxxxxxx.

URL: https://projecteuler.net/problem=199
"""
from typing import Any

euler_problem: int = 199
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'iterations': 3}, 'answer': None},
    {'category': 'main', 'input': {'iterations': 10}, 'answer': None},
    {'category': 'extra', 'input': {'iterations': 12}, 'answer': None},
]
encrypted: str = (
    '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'
    'giGMdoFkVTlBE5xHiJSaPsV04HTtIkPAWfcSUQ=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
