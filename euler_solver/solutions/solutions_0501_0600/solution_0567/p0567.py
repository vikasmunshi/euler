#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 567: Reciprocal Games I.

Problem Statement:
    Tom has built a random generator that is connected to a row of n light bulbs.
    Whenever the random generator is activated each of the n lights is turned on
    with the probability of 1/2, independently of its former state or the state of
    the other light bulbs.

    While discussing with his friend Jerry how to use his generator, they invent
    two different games, they call the reciprocal games: Both games consist of n turns.
    Each turn is started by choosing a number k randomly between (and including) 1 and n,
    with equal probability of 1/n for each number, while the possible win for that turn
    is the reciprocal of k, that is 1/k.

    In game A, Tom activates his random generator once in each turn. If the number of lights
    turned on is the same as the previously chosen number k, Jerry wins and gets 1/k,
    otherwise he will receive nothing for that turn. Jerry's expected win after playing
    the total game A consisting of n turns is called J_A(n). For example J_A(6)=0.39505208,
    rounded to 8 decimal places.

    For each turn in game B, after k has been randomly selected, Tom keeps reactivating
    his random generator until exactly k lights are turned on. After that Jerry takes over
    and reactivates the random generator until he, too, has generated a pattern with exactly
    k lights turned on. If this pattern is identical to Tom's last pattern, Jerry wins and
    gets 1/k, otherwise he will receive nothing. Jerry's expected win after the total game B
    consisting of n turns is called J_B(n). For example J_B(6)=0.43333333, rounded to 8 decimal places.

    Let S(m) = sum from n=1 to m of (J_A(n)+J_B(n)). For example S(6)=7.58932292, rounded
    to 8 decimal places.

    Find S(123456789), rounded to 8 decimal places.

URL: https://projecteuler.net/problem=567
"""
from typing import Any

euler_problem: int = 567
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'m': 6}, 'answer': None},
    {'category': 'main', 'input': {'m': 123456789}, 'answer': None},
]
encrypted: str = (
    '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'
    'x8DejOCJKitJJDfRT6pyaA=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
