#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 895: Gold & Silver Coin Game II.

Problem Statement:
    Gary and Sally play a game using gold and silver coins arranged into a number of
    vertical stacks, alternating turns. On Gary's turn he chooses a gold coin and
    removes it from the game along with any other coins sitting on top. Sally does
    the same on her turn by removing a silver coin. The first player unable to make
    a move loses.

    An arrangement is called fair if the person moving first, whether it be Gary or
    Sally, will lose the game if both play optimally.

    An arrangement is called balanced if the number of gold and silver coins are equal.

    Define G(m) to be the number of fair and balanced arrangements consisting of three
    non-empty stacks, each not exceeding m in size. Different orderings of the stacks
    are to be counted separately, so G(2)=6 due to the following six arrangements:

    You are also given G(5)=348 and G(20)=125825982708.

    Find G(9898) giving your answer modulo 989898989.

URL: https://projecteuler.net/problem=895
"""
from typing import Any

euler_problem: int = 895
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'max_limit': 9898}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
