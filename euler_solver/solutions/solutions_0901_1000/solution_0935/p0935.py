#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 935: Rolling Square.

Problem Statement:
    A square of side length b<1 is rolling around the inside of a larger square
    of side length 1, always touching the larger square but without sliding.
    Initially the two squares share a common corner. At each step, the small
    square rotates clockwise about a corner that touches the large square,
    until another of its corners touches the large square.

    For some values of b, the small square may return to its initial position
    after several steps. For example, when b = 1/2, this happens in 4 steps;
    and for b = 5/13 it happens in 24 steps.

    Let F(N) be the number of different values of b for which the small square
    first returns to its initial position within at most N steps. For example,
    F(6) = 4, with the corresponding b values:
        1/2,
        2 - sqrt(2),
        2 + sqrt(2) - sqrt(2 + 4*sqrt(2)),
        8 - 5*sqrt(2) + 4*sqrt(3) - 3*sqrt(6),
    the first three in 4 steps and the last one in 6 steps.
    Note that it does not matter whether the small square returns to its original
    orientation. Also F(100) = 805.

    Find F(10^8).

URL: https://projecteuler.net/problem=935
"""
from typing import Any

euler_problem: int = 935
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'max_steps': 100000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'aIbxldDiIXsBCPGK'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
