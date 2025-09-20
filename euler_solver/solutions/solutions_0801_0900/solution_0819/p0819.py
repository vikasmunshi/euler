#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 819: Iterative Sampling.

Problem Statement:
    Given an n-tuple of numbers another n-tuple is created where each element of
    the new n-tuple is chosen randomly from the numbers in the previous n-tuple.
    For example, given (2,2,3) the probability that 2 occurs in the first position
    in the next 3-tuple is 2/3. The probability of getting all 2's would be 8/27
    while the probability of getting the same 3-tuple (in any order) would be 4/9.

    Let E(n) be the expected number of steps starting with (1, 2, ..., n) and
    ending with all numbers being the same.

    You are given E(3) = 27/7 and E(5) = 468125/60701 approx 7.711982 rounded to
    6 digits after the decimal place.

    Find E(10^3). Give the answer rounded to 6 digits after the decimal place.

URL: https://projecteuler.net/problem=819
"""
from typing import Any

euler_problem: int = 819
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 3}, 'answer': None},
    {'category': 'main', 'input': {'n': 1000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
