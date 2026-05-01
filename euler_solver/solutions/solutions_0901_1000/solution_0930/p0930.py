#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 930: The Gathering.

Problem Statement:
    Given n≥2 bowls arranged in a circle, m≥2 balls are distributed amongst them.
    Initially the balls are distributed randomly: for each ball, a bowl is chosen
    equiprobably and independently of the other balls. After this is done, we start
    the following process:

        1. Choose one of the m balls equiprobably at random.
        2. Choose a direction to move - either clockwise or anticlockwise - again
           equiprobably at random.
        3. Move the chosen ball to the neighbouring bowl in the chosen direction.
        4. Return to step 1.

    This process stops when all the m balls are located in the same bowl. Note that
    this may be after zero steps, if the balls happen to have been initially distributed
    all in the same bowl.

    Let F(n, m) be the expected number of times we move a ball before the process stops.
    For example, F(2, 2) = 1/2, F(3, 2) = 4/3, F(2, 3) = 9/4, and F(4, 5) = 6875/24.

    Let G(N, M) = sum_{n=2}^N sum_{m=2}^M F(n, m). For example, G(3, 3) = 137/12 and
    G(4, 5) = 6277/12. You are also given that G(6, 6) ≈ 1.681521567954e4 in scientific
    format with 12 significant digits after the decimal point.

    Find G(12, 12). Give your answer in scientific format with 12 significant digits
    after the decimal point.

URL: https://projecteuler.net/problem=930
"""
from typing import Any

euler_problem: int = 930
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}, 'answer': None},
]
encrypted: str = (
    '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'
    'hDhyIQV1K/I3S0eMzXE8vQ=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
