#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 901: Well Drilling.

Problem Statement:
    A driller drills for water. At each iteration the driller chooses a depth d
    (a positive real number), drills to this depth and then checks if water was
    found. If so, the process terminates. Otherwise, a new depth is chosen and a
    new drilling starts from the ground level in a new location nearby.

    Drilling to depth d takes exactly d hours. The groundwater depth is constant
    in the relevant area and its distribution is known to be an exponential
    random variable with expected value of 1. In other words, the probability that
    the groundwater is deeper than d is e^-d.

    Assuming an optimal strategy, find the minimal expected drilling time in hours
    required to find water. Give your answer rounded to 9 places after the decimal
    point.

URL: https://projecteuler.net/problem=901
"""
from typing import Any

euler_problem: int = 901
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
