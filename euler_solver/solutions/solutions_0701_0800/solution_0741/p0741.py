#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 741: Binary Grid Colouring.

Problem Statement:
    Let f(n) be the number of ways an n×n square grid can be coloured, each cell
    either black or white, such that each row and each column contains exactly two
    black cells.

    For example, f(4)=90, f(7) = 3110940 and f(8) = 187530840.

    Let g(n) be the number of colourings in f(n) that are unique up to rotations
    and reflections.

    You are given g(4)=20, g(7) = 390816 and g(8) = 23462347 giving
    g(7)+g(8) = 23853163.

    Find g(7^7) + g(8^8). Give your answer modulo 1000000007.

URL: https://projecteuler.net/problem=741
"""
from typing import Any

euler_problem: int = 741
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 4}, 'answer': None},
    {'category': 'main', 'input': {'n': 823543}, 'answer': None},
    {'category': 'extra', 'input': {'n': 16777216}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
