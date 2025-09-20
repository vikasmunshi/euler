#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 933: Paper Cutting.

Problem Statement:
    Starting with one piece of integer-sized rectangle paper, two players make moves in turn.
    A valid move consists of choosing one piece of paper and cutting it both horizontally and
    vertically, so that it becomes four pieces of smaller rectangle papers, all of which are
    integer-sized. The player that does not have a valid move loses the game.

    Let C(w, h) be the number of winning moves for the first player, when the original paper
    has size w x h. For example, C(5,3) = 4, with the four winning moves shown below.

    Also write D(W, H) = sum_{w=2}^W sum_{h=2}^H C(w, h). You are given that D(12, 123) = 327398.

    Find D(123, 1234567).

URL: https://projecteuler.net/problem=933
"""
from typing import Any

euler_problem: int = 933
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'W': 123, 'H': 1234567}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
