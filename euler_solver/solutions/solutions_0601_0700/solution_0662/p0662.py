#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 662: Fibonacci Paths.

Problem Statement:
    Alice walks on a lattice grid. She can step from one lattice point A (a,b) to another
    B (a+x,b+y) providing distance AB = sqrt(x^2+y^2) is a Fibonacci number {1,2,3,5,8,13,...}
    and x >= 0, y >= 0.

    In the lattice grid below Alice can step from the blue point to any of the red points.

    Let F(W,H) be the number of paths Alice can take from (0,0) to (W,H).
    You are given F(3,4) = 278 and F(10,10) = 215846462.

    Find F(10000,10000) modulo 1000000007.

URL: https://projecteuler.net/problem=662
"""
from typing import Any

euler_problem: int = 662
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'W': 3, 'H': 4}, 'answer': None},
    {'category': 'main', 'input': {'W': 10000, 'H': 10000}, 'answer': None},
]
encrypted: str = (
    '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'
    'hSogBF5sHMIKT7zOdd0NF6r9PHwFeDmn'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
