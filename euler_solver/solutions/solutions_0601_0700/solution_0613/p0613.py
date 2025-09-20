#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 613: Pythagorean Ant.

Problem Statement:
    Dave is doing his homework on the balcony and, preparing a presentation about
    Pythagorean triangles, has just cut out a triangle with side lengths 30cm, 40cm
    and 50cm from some cardboard, when a gust of wind blows the triangle down into
    the garden.

    Another gust blows a small ant straight onto this triangle. The poor ant is
    completely disoriented and starts to crawl straight ahead in random direction
    in order to get back into the grass.

    Assuming that all possible positions of the ant within the triangle and all
    possible directions of moving on are equiprobable, what is the probability that
    the ant leaves the triangle along its longest side?
    Give your answer rounded to 10 digits after the decimal point.

URL: https://projecteuler.net/problem=613
"""
from typing import Any

euler_problem: int = 613
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
