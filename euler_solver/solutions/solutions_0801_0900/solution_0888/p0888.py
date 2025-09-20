#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 888: 1249 Nim.

Problem Statement:
    Two players play a game with a number of piles of stones, alternating turns. Each turn a
    player can choose to remove 1, 2, 4, or 9 stones from a single pile; or alternatively they
    can choose to split a pile containing two or more stones into two non-empty piles. The
    winner is the player who removes the last stone.

    A collection of piles is called a losing position if the player to move cannot force a win
    with optimal play. Define S(N, m) to be the number of distinct losing positions arising
    from m piles of stones where each pile contains from 1 to N stones. Two positions are
    considered equivalent if they consist of the same pile sizes. That is, the order of the
    piles does not matter.

    You are given S(12,4)=204 and S(124,9)=2259208528408.

    Find S(12491249,1249). Give your answer modulo 912491249.

URL: https://projecteuler.net/problem=888
"""
from typing import Any

euler_problem: int = 888
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 12, 'pile_count': 4}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 12491249, 'pile_count': 1249}, 'answer': None},
]
encrypted: str = (
    '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'
    'VWtcInzzV7yGYUaCU6Mf7GDfuY5owpr0/eWyPw=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
