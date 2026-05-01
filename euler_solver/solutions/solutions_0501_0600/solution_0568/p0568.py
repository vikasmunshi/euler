#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 568: Reciprocal Games II.

Problem Statement:
    Tom has built a random generator that is connected to a row of n light bulbs.
    Whenever the random generator is activated each of the n lights is turned on
    with the probability of 1/2, independently of its former state or the state of
    the other light bulbs.

    While discussing with his friend Jerry how to use his generator, they invent two
    different games, they call the reciprocal games:
    Both games consist of n turns. Each turn is started by choosing a number k randomly
    between (and including) 1 and n, with equal probability of 1/n for each number,
    while the possible win for that turn is the reciprocal of k, that is 1/k.

    In game A, Tom activates his random generator once in each turn. If the number of
    lights turned on is the same as the previously chosen number k, Jerry wins and gets
    1/k, otherwise he will receive nothing for that turn. Jerry's expected win after
    playing the total game A consisting of n turns is called J_A(n). For example J_A(6)=0.39505208,
    rounded to 8 decimal places.

    For each turn in game B, after k has been randomly selected, Tom keeps reactivating
    his random generator until exactly k lights are turned on. After that Jerry takes
    over and reactivates the random generator until he, too, has generated a pattern with
    exactly k lights turned on. If this pattern is identical to Tom's last pattern, Jerry
    wins and gets 1/k, otherwise he will receive nothing. Jerry's expected win after the
    total game B consisting of n turns is called J_B(n). For example J_B(6)=0.43333333,
    rounded to 8 decimal places.

    Let D(n)=J_B(n)−J_A(n). For example, D(6) = 0.03828125.

    Find the 7 most significant digits of D(123456789) after removing all leading zeros.
    (If, for example, we had asked for the 7 most significant digits of D(6), the answer
    would have been 3828125.)

URL: https://projecteuler.net/problem=568
"""
from typing import Any

euler_problem: int = 568
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 6}, 'answer': None},
    {'category': 'main', 'input': {'n': 123456789}, 'answer': None},
]
encrypted: str = (
    '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'
    'F6XsMqwY4RQ='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
