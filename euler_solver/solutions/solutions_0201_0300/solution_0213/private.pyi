#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 213: Flea Circus.

Problem Statement:
    A 30 x 30 grid of squares contains 900 fleas, initially one flea per
    square.
    When a bell is rung, each flea jumps to an adjacent square at random
    (usually 4 possibilities, except for fleas on the edge of the grid or at
    the corners).

    What is the expected number of unoccupied squares after 50 rings of the
    bell? Give your answer rounded to six decimal places.

Solution Approach:
    Use linearity of expectation: the expected number of empty squares is the
    sum over all squares of the probability that that square is empty after R
    rings.
    Model each flea as an independent Markov chain on the 30 x 30 grid. Compute
    transition probabilities p_{i->j}^{(R)} by raising the 900x900 transition
    matrix to the R-th power or by using spectral methods (discrete cosine
    transforms) exploiting the grid structure.
    For each target square s compute prod_{start i}(1 - p_{i->s}) and sum over
    s to get the expectation.
    Complexity: naive matrix powering is roughly O(n^3 log R) for n=900; using
    spectral or separable methods reduces time and memory. Use double precision
    and round the final expected value to six decimals.

Answer: ...
URL: https://projecteuler.net/problem=213
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 213
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'rings': 1}},
    {'category': 'main', 'input': {'rings': 50}},
    {'category': 'extra', 'input': {'rings': 100}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_flea_circus_p0213_s0(*, rings: int) -> int: ...


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))