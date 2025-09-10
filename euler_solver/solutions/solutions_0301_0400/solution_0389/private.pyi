#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 389: Platonic Dice.

Problem Statement:
    An unbiased single 4-sided die is thrown and its value, T, is noted.
    T unbiased 6-sided dice are thrown and their scores are added together.
    The sum, C, is noted.
    C unbiased 8-sided dice are thrown and their scores are added together.
    The sum, O, is noted.
    O unbiased 12-sided dice are thrown and their scores are added together.
    The sum, D, is noted.
    D unbiased 20-sided dice are thrown and their scores are added together.
    The sum, I, is noted.
    Find the variance of I, and give your answer rounded to 4 decimal places.

Solution Approach:
    Use the law of total variance for random sums: for S = sum_{i=1}^N X_i with iid X_i
    independent of N, Var(S) = E[N]Var(X) + (E[X])^2 Var(N).
    Compute mean and variance for an s-sided fair die: mean = (s+1)/2, var = (s^2-1)/12.
    Propagate mean and variance iteratively T -> C -> O -> D -> I using the formula.
    All computations are exact-rational or floating arithmetic; overall complexity O(1).

Answer: ...
URL: https://projecteuler.net/problem=389
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 389
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_platonic_dice_p0389_s0() -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))