#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 412: Gnomon Numbering.

Problem Statement:
    For integers m, n (0 ≤ n < m), let L(m, n) be an m by m grid with the top-right n by
    n grid removed.

    For example, L(5, 3) looks like this:

    We want to number each cell of L(m, n) with consecutive integers 1, 2, 3, ... such that
    the number in every cell is smaller than the number below it and to the left of it.

    For example, two valid numberings of L(5, 3) are given.

    Let LC(m, n) be the number of valid numberings of L(m, n).
    It can be verified that LC(3, 0) = 42, LC(5, 3) = 250250, LC(6, 3) = 406029023400,
    and LC(10, 5) mod 76543217 = 61251715.

    Find LC(10000, 5000) mod 76543217.

URL: https://projecteuler.net/problem=412
"""
from typing import Any

euler_problem: int = 412
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'m': 5, 'n': 3}, 'answer': None},
    {'category': 'main', 'input': {'m': 10000, 'n': 5000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
