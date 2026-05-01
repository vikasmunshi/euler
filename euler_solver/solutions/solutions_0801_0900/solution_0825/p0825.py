#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 825: Chasing Game.

Problem Statement:
    Two cars are on a circular track of total length 2n, facing the same direction,
    initially distance n apart.
    They move in turn. At each turn, the moving car will advance a distance of 1, 2 or 3,
    with equal probabilities.
    The chase ends when the moving car reaches or goes beyond the position of the other car.
    The moving car is declared the winner.

    Let S(n) be the difference between the winning probabilities of the two cars.
    For example, when n = 2, the winning probabilities of the two cars are 9/11 and 2/11,
    and thus S(2) = 7/11.

    Let T(N) = sum from n = 2 to N of S(n).

    You are given that T(10) = 2.38235282 rounded to 8 digits after the decimal point.

    Find T(10^14), rounded to 8 digits after the decimal point.

URL: https://projecteuler.net/problem=825
"""
from typing import Any

euler_problem: int = 825
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 100000000000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'Xp+5sHTtG3LZuqdm8tIOvbmARLw='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
