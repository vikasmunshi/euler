#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 371: Licence Plates.

Problem Statement:
    Oregon licence plates consist of three letters followed by a three
    digit number (each digit can be from [0..9]). While driving to work
    Seth plays the following game: Whenever the numbers of two licence
    plates seen on his trip add to 1000 that's a win.

    E.g. MIC-012 and HAN-988 is a win and RYU-500 and SET-500 too (as
    long as he sees them in the same trip).

    Find the expected number of plates he needs to see for a win.
    Give your answer rounded to 8 decimal places behind the decimal
    point.

    Note: We assume that each licence plate seen is equally likely to
    have any three digit number on it.

URL: https://projecteuler.net/problem=371
"""
from typing import Any

euler_problem: int = 371
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'num_values': 10}, 'answer': None},
    {'category': 'main', 'input': {'num_values': 1000}, 'answer': None},
    {'category': 'extra', 'input': {'num_values': 10000}, 'answer': None},
]
encrypted: str = (
    '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'
    'bi+jVY/G9N0='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
