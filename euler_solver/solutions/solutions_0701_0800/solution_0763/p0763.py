#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 763: Amoebas in a 3D Grid.

Problem Statement:
    Consider a three dimensional grid of cubes. An amoeba in cube (x, y, z) can
    divide itself into three amoebas to occupy the cubes (x + 1, y, z), (x, y + 1, z)
    and (x, y, z + 1), provided these cubes are empty.

    Originally there is only one amoeba in the cube (0, 0, 0). After N divisions
    there will be 2N+1 amoebas arranged in the grid. An arrangement may be reached
    in several different ways but it is only counted once. Let D(N) be the number
    of different possible arrangements after N divisions.

    For example, D(2) = 3, D(10) = 44499, D(20)=9204559704 and the last nine digits
    of D(100) are 780166455.

    Find D(10,000), enter the last nine digits as your answer.

URL: https://projecteuler.net/problem=763
"""
from typing import Any

euler_problem: int = 763
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 2}, 'answer': None},
    {'category': 'main', 'input': {'n': 10000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
