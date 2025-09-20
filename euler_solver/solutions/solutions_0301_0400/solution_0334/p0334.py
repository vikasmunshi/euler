#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 334: Spilling the Beans.

Problem Statement:
    In Plato's heaven, there exist an infinite number of bowls in a straight
    line. Each bowl either contains some or none of a finite number of beans.
    A child plays a game, which allows only one kind of move: removing two
    beans from any bowl, and putting one in each of the two adjacent bowls.
    The game ends when each bowl contains either one or no beans.

    For example, consider two adjacent bowls containing 2 and 3 beans
    respectively, all other bowls being empty. The following eight moves will
    finish the game.

    You are given the following sequences:
    t0 = 123456.
    t_i = t_{i-1}/2 if t_{i-1} is even;
    otherwise t_i = floor(t_{i-1}/2) xor 926252.
    Here floor(x) is the floor function and xor is the bitwise XOR operator.
    b_i = (t_i mod 2^11) + 1.

    The first two terms of the last sequence are b1 = 289 and b2 = 145.
    If we start with b1 and b2 beans in two adjacent bowls, 3419100 moves
    would be required to finish the game.

    Consider now 1500 adjacent bowls containing b1, b2, ..., b1500 beans
    respectively, all other bowls being empty. Find how many moves it takes
    before the game ends.

URL: https://projecteuler.net/problem=334
"""
from typing import Any

euler_problem: int = 334
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'num_bowls': 2}, 'answer': None},
    {'category': 'main', 'input': {'num_bowls': 1500}, 'answer': None},
    {'category': 'extra', 'input': {'num_bowls': 5000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
