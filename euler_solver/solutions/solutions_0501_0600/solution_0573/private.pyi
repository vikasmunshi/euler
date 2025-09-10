#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 573: Unfair Race.

Problem Statement:
    n runners in very different training states want to compete in a race.
    Each one of them is given a different starting number k (1 ≤ k ≤ n)
    according to the runner's (constant) individual racing speed being
    v_k = k/n.

    In order to give the slower runners a chance to win the race, n
    different starting positions are chosen randomly (with uniform
    distribution) and independently from each other within the racing track
    of length 1. After this, the starting position nearest to the goal is
    assigned to runner 1, the next nearest starting position to runner 2
    and so on, until finally the starting position furthest away from the
    goal is assigned to runner n. The winner of the race is the runner who
    reaches the goal first.

    Interestingly, the expected running time for the winner is 1/2,
    independently of the number of runners. Moreover, while it can be
    shown that all runners will have the same expected running time of n/(n+1),
    the race is still unfair, since the winning chances may differ
    significantly for different starting numbers:

    Let P_{n,k} be the probability for runner k to win a race with n runners
    and E_n = sum_{k=1}^n k P_{n,k} be the expected starting number of the
    winner in that race. It can be shown that, for example,
    P_{3,1}=4/9, P_{3,2}=2/9, P_{3,3}=1/3 and E_3=17/9 for a race with 3
    runners.
    You are given that E_4=2.21875, E_5=2.5104 and E_10=3.66021568.

    Find E_1000000 rounded to 4 digits after the decimal point.

Solution Approach:
    The problem combines probability with order statistics and race dynamics.
    Key ideas include understanding the uniform random starting positions,
    ordering them, and computing winning probabilities based on relative
    speeds and placements.
    Techniques may involve integration over distributions, combinatorics of
    assignments, and potentially approximations or asymptotic formulas for
    large n. Efficient computation will likely hinge on analytical results
    or iterative numerical methods for large-scale sums.

Answer: ...
URL: https://projecteuler.net/problem=573
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 573
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 3}},
    {'category': 'main', 'input': {'n': 1000000}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_unfair_race_p0573_s0(*, n: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))