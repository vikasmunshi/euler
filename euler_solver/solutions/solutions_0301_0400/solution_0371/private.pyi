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

Solution Approach:
    Model the three-digit numbers as independent uniform draws from
    0..num_values-1 (for the original problem num_values=1000). A win
    occurs when a drawn number and a previously seen number sum to
    num_values. Group numbers into complementary pairs and a possible
    self-pair (e.g. 500+500). Compute P(no win after t draws) by dynamic
    programming over pairs and the special self-pair, or by counting
    allowed sequences. Then use E[T] = sum_{t>=0} P(T>t) and truncate when
    tail probabilities are negligible. Time/space: O(t_max * num_pairs).

Answer: ...
URL: https://projecteuler.net/problem=371
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 371
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'num_values': 10}},
    {'category': 'main', 'input': {'num_values': 1000}},
    {'category': 'extra', 'input': {'num_values': 10000}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_licence_plates_p0371_s0(*, num_values: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))