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

Solution Approach:
    Model the process as a Markov chain on the distribution states of balls on bowls.
    Use probability and expectation theory to derive linear equations for F(n,m).
    Employ symmetry and combinatorics to reduce state space size.
    Use dynamic programming or matrix inversion to compute F(n,m) efficiently.
    Finally, sum over all required n,m pairs for G(N,M).
    Expect polynomial-time complexity in terms of N and M due to state space reduction.

Answer: ...
URL: https://projecteuler.net/problem=930
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 930
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_the_gathering_p0930_s0() -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))