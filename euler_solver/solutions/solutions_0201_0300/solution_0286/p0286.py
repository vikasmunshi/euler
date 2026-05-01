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

URL: https://projecteuler.net/problem=286
"""
from typing import Any

euler_problem: int = 286
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_distance': 5, 'target_score': 2, 'probability': 0.1}, 'answer': None},
    {'category': 'main', 'input': {'max_distance': 50, 'target_score': 20, 'probability': 0.02}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
