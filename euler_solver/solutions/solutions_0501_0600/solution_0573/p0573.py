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

URL: https://projecteuler.net/problem=573
"""
from typing import Any

euler_problem: int = 573
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 3}, 'answer': None},
    {'category': 'main', 'input': {'n': 1000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
