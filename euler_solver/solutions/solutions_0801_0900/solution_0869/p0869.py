#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 869: Prime Guessing.

Problem Statement:
    A prime is drawn uniformly from all primes not exceeding N. The prime is written
    in binary notation, and a player tries to guess it bit-by-bit starting at the
    least significant bit. The player scores one point for each bit they guess
    correctly. Immediately after each guess, the player is informed whether their
    guess was correct, and also whether it was the last bit in the number - in which
    case the game is over.

    Let E(N) be the expected number of points assuming that the player always
    guesses to maximize their score. For example, E(10)=2, achievable by always
    guessing "1". You are also given E(30)=2.9.

    Find E(10^8). Give your answer rounded to eight digits after the decimal point.

URL: https://projecteuler.net/problem=869
"""
from typing import Any

euler_problem: int = 869
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 30}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 100000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'sKm3vpNxOenwf3dqNKociw=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
