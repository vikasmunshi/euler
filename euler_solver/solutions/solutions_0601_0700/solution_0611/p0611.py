#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 611: Hallway of Square Steps.

Problem Statement:
    Peter moves in a hallway with N + 1 doors consecutively numbered from 0
    through N. All doors are initially closed. Peter starts in front of door 0,
    and repeatedly performs the following steps:
        1. First, he walks a positive square number of doors away from his position.
        2. Then he walks another, larger square number of doors away from his new position.
        3. He toggles the door he faces (opens it if closed, closes it if open).
        4. And finally returns to door 0.

    We call an action any sequence of those steps. Peter never performs the exact
    same action twice, and makes sure to perform all possible actions that don't
    bring him past the last door.

    Let F(N) be the number of doors that are open after Peter has performed all
    possible actions. You are given that F(5) = 1, F(100) = 27, F(1000) = 233
    and F(10^6) = 112168.

    Find F(10^12).

URL: https://projecteuler.net/problem=611
"""
from typing import Any

euler_problem: int = 611
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 1000000000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
