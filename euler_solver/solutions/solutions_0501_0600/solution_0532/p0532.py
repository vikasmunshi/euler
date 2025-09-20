#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 532: Nanobots on Geodesics.

Problem Statement:
    Bob is a manufacturer of nanobots and wants to impress his customers by giving
    them a ball coloured by his new nanobots as a present.

    His nanobots can be programmed to select and locate exactly one other bot
    precisely and, after activation, move towards this bot along the shortest possible
    path and draw a coloured line onto the surface while moving. Placed on a plane,
    the bots will start to move towards their selected bots in a straight line. In
    contrast, being placed on a ball, they will start to move along a geodesic as
    the shortest possible path. However, in both cases, whenever their target moves
    they will adjust their direction instantaneously to the new shortest possible
    path. All bots will move at the same speed after their simultaneous activation
    until each bot reaches its goal.

    Now Bob places n bots on the ball (with radius 1) equidistantly on a small circle
    with radius 0.999 and programs each of them to move toward the next nanobot
    sitting counterclockwise on that small circle. After activation, the bots move
    in a sort of spiral until they finally meet at one point on the ball.

    Using three bots, Bob finds that every bot will draw a line of length 2.84,
    resulting in a total length of 8.52 for all three bots, each time rounded to
    two decimal places. The coloured ball looks like this:

    In order to show off a little with his presents, Bob decides to use just enough
    bots to make sure that the line each bot draws is longer than 1000. What is the
    total length of all lines drawn with this number of bots, rounded to two decimal
    places?

URL: https://projecteuler.net/problem=532
"""
from typing import Any

euler_problem: int = 532
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 3}, 'answer': None},
    {'category': 'main', 'input': {}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
