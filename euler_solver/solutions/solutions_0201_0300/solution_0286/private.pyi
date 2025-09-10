#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 286: Scoring Probabilities.

Problem Statement:
    Barbara is a mathematician and a basketball player. She has found that the
    probability of scoring a point when shooting from a distance x is exactly
    (1 - x / q), where q is a real constant greater than 50.

    During each practice run, she takes shots from distances x = 1, x = 2, ...
    x = 50 and, according to her records, she has precisely a 2% chance to
    score a total of exactly 20 points.

    Find q and give your answer rounded to 10 decimal places.

Solution Approach:
    Model each shot x as an independent Bernoulli trial with success prob
    p_x = 1 - x / q. The probability of exactly k successes is the coefficient
    of z^k in the polynomial product over x of ((1 - p_x) + p_x*z).
    Compute that coefficient by dynamic programming (convolution) in O(n*k).
    Treat P(q) = Prob_exact_k(q) and solve P(q) = target_prob for q > 50 by
    a monotone root-finding method (bisection or Newton with safe bracketing).
    Each probability evaluation costs O(n*k); overall complexity is
    O(iterations * n * k) time and O(k) space.

Answer: ...
URL: https://projecteuler.net/problem=286
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 286
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_distance': 5, 'target_score': 2, 'probability': 0.1}},
    {'category': 'main', 'input': {'max_distance': 50, 'target_score': 20, 'probability': 0.02}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_scoring_probabilities_p0286_s0(*, max_distance: int, target_score: int, probability: float) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))