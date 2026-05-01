#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 709: Even Stevens.

Problem Statement:
    Every day for the past n days Even Stevens brings home his groceries in a plastic bag.
    He stores these plastic bags in a cupboard. He either puts the plastic bag into the
    cupboard with the rest, or else he takes an even number of the existing bags (which may
    either be empty or previously filled with other bags themselves) and places these into
    the current bag.

    After 4 days there are 5 possible packings and if the bags are numbered 1 (oldest), 2, 3,
    4, they are:
        Four empty bags,
        1 and 2 inside 3, 4 empty,
        1 and 3 inside 4, 2 empty,
        1 and 2 inside 4, 3 empty,
        2 and 3 inside 4, 1 empty.

    Note that 1, 2, 3 inside 4 is invalid because every bag must contain an even number of bags.

    Define f(n) to be the number of possible packings of n bags. Hence f(4)=5. You are also
    given f(8)=1385.

    Find f(24680) giving your answer modulo 1020202009.

URL: https://projecteuler.net/problem=709
"""
from typing import Any

euler_problem: int = 709
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 4}, 'answer': None},
    {'category': 'main', 'input': {'n': 24680}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
