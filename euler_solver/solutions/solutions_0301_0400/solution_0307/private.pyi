#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 307: Chip Defects.

Problem Statement:
    k defects are randomly distributed amongst n integrated-circuit chips
    produced by a factory (any number of defects may be found on a chip and
    each defect is independent of the other defects).

    Let p(k, n) represent the probability that there is a chip with at least
    3 defects. For instance p(3,7) ≈ 0.0204081633.

    Find p(20,000, 1,000,000) and give your answer rounded to 10 decimal places
    in the form 0.abcdefghij.

Solution Approach:
    Model: each defect independently lands on one of n chips, so counts per
    chip follow a multinomial; for large n use Poisson approx with λ = k/n.
    Per-chip prob of fewer than 3 defects is sum_{i=0..2} e^{-λ} λ^i / i!.
    The desired probability is 1 - (prob_per_chip_less_than_3)^n.
    Compute using high-precision arithmetic and logarithms for numerical
    stability (use Decimal or an MP library); time O(1), space O(1).

Answer: ...
URL: https://projecteuler.net/problem=307
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 307
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'k': 3, 'n': 7}},
    {'category': 'main', 'input': {'k': 20000, 'n': 1000000}},
    {'category': 'extra', 'input': {'k': 200000, 'n': 1000000}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_chip_defects_p0307_s0(*, k: int, n: int) -> int: ...


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))