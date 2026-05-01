#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 503: Compromise or Persist.

Problem Statement:
    Alice is playing a game with n cards numbered 1 to n.

    A game consists of iterations of the following steps.
    (1) Alice picks one of the cards at random.
    (2) Alice cannot see the number on it. Instead, Bob, one of her friends,
        sees the number and tells Alice how many previously-seen numbers are
        bigger than the number which he is seeing.
    (3) Alice can end or continue the game. If she decides to end, the number
        becomes her score. If she decides to continue, the card is removed from
        the game and she returns to (1). If there is no card left, she is forced
        to end the game.

    Let F(n) be Alice's expected score if she takes the optimized strategy to
    minimize her score.

    For example, F(3) = 5/3. At the first iteration, she should continue the
    game. At the second iteration, she should end the game if Bob says that
    one previously-seen number is bigger than the number which he is seeing,
    otherwise she should continue the game.

    We can also verify that F(4) = 15/8 and F(10) ≈ 2.5579365079.

    Find F(10^6). Give your answer rounded to 10 decimal places behind the
    decimal point.

URL: https://projecteuler.net/problem=503
"""
from typing import Any

euler_problem: int = 503
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 3}, 'answer': None},
    {'category': 'dev', 'input': {'n': 4}, 'answer': None},
    {'category': 'main', 'input': {'n': 1000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'bQaNH4mODVIkdmaiuc6QE79WRKrDzpNQ'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
