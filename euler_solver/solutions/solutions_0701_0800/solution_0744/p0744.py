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

URL: https://projecteuler.net/problem=744
"""
from typing import Any

euler_problem: int = 744
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 6, 'p': 0.5}, 'answer': None},
    {'category': 'main', 'input': {'n': 100000000000, 'p': 0.4999}, 'answer': None},
    {'category': 'extra', 'input': {'n': 10000, 'p': 0.3}, 'answer': None},
]
encrypted: str = (
    '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'
    'zJg8bFbT03FNsBOV'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
