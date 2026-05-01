#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 194: Coloured Configurations.

Problem Statement:
    Consider graphs built with the units A and B, where the units are glued
    along the vertical edges as in the figure.

    A configuration of type (a, b, c) is a graph thus built of a units A and
    b units B, where the graph's vertices are coloured using up to c colours,
    so that no two adjacent vertices have the same colour.
    The compound graph shown above is an example of a configuration of type
    (2,2,6), in fact of type (2,2,c) for all c >= 4.

    Let N(a, b, c) be the number of configurations of type (a, b, c). For
    example, N(1,0,3) = 24, N(0,2,4) = 92928 and N(2,2,3) = 20736.

    Find the last 8 digits of N(25,75,1984).

URL: https://projecteuler.net/problem=194
"""
from typing import Any

euler_problem: int = 194
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'a': 1, 'b': 0, 'c': 3}, 'answer': None},
    {'category': 'main', 'input': {'a': 25, 'b': 75, 'c': 1984}, 'answer': None},
    {'category': 'extra', 'input': {'a': 2, 'b': 2, 'c': 6}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
