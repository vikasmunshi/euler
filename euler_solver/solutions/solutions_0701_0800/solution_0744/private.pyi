#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 744: What? Where? When?.

Problem Statement:
    "What? Where? When?" is a TV game show in which a team of experts attempt to
    answer questions. The following is a simplified version of the game.

    It begins with 2n+1 envelopes. 2n of them contain a question and one contains a
    RED card.

    In each round one of the remaining envelopes is randomly chosen. If the envelope
    contains the RED card the game ends. If the envelope contains a question the expert
    gives their answer. If their answer is correct they earn one point, otherwise the
    viewers earn one point. The game ends normally when either the expert obtains n
    points or the viewers obtain n points.

    Assuming that the expert provides the correct answer with a fixed probability p,
    let f(n,p) be the probability that the game ends normally (i.e. RED card never
    turns up).

    You are given (rounded to 10 decimal places) that
    f(6,1/2) = 0.2851562500,
    f(10,3/7) = 0.2330040743,
    f(10^4,0.3) = 0.2857499982.

    Find f(10^11,0.4999). Give your answer rounded to 10 places behind the decimal point.

Solution Approach:
    Model the problem as a Markov process or use dynamic programming to track the
    probabilities of scoring points by the expert or viewers before the RED card is
    drawn. Use combinatorics and probability theory to derive a formula or
    recurrence relation for f(n,p). Efficient handling for large n (up to 10^11)
    likely requires approximations or analytic solutions exploiting symmetry and
    limiting behavior.

Answer: ...
URL: https://projecteuler.net/problem=744
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 744
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 6, 'p': 0.5}},
    {'category': 'main', 'input': {'n': 10**11, 'p': 0.4999}},
    {'category': 'extra', 'input': {'n': 10**4, 'p': 0.3}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_what_where_when_p0744_s0(*, n: int, p: float) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))