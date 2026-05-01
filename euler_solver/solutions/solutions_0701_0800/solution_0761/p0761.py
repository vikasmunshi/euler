#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 761: Runner and Swimmer.

Problem Statement:
    Two friends, a runner and a swimmer, are playing a sporting game: The swimmer is
    swimming within a circular pool while the runner moves along the pool edge.
    While the runner tries to catch the swimmer at the very moment that the swimmer
    leaves the pool, the swimmer tries to reach the edge before the runner arrives there.
    They start the game with the swimmer located in the middle of the pool, while the
    runner is located anywhere at the edge of the pool.

    We assume that the swimmer can move with any velocity up to 1 in any direction
    and the runner can move with any velocity up to v in either direction around the
    edge of the pool. Moreover we assume that both players can react immediately
    to any change of movement of their opponent.

    Assuming optimal strategy of both players, it can be shown that the swimmer can
    always win by escaping the pool at some point at the edge before the runner gets
    there, if v is less than the critical speed V_Circle ≈ 4.60333885 and can never
    win if v > V_Circle.

    Now the two players play the game in a perfectly square pool. Again the swimmer
    starts in the middle of the pool, while the runner starts at the midpoint of one
    of the edges of the pool. It can be shown that the critical maximal speed of the
    runner below which the swimmer can always escape and above which the runner can
    always catch the swimmer when trying to leave the pool is V_Square ≈ 5.78859314.

    At last, both players decide to play the game in a pool in the form of regular
    hexagon. Giving the same conditions as above, with the swimmer starting in the
    middle of the pool and the runner at the midpoint of one of the edges of the pool,
    find the critical maximal speed V_Hexagon of the runner, below which the swimmer
    can always escape and above which the runner can always catch the swimmer.
    Give your answer rounded to 8 digits after the decimal point.

URL: https://projecteuler.net/problem=761
"""
from typing import Any

euler_problem: int = 761
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}, 'answer': None},
]
encrypted: str = (
    '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'
    '9xsLHoJQb8SbP9DyuEtWbDT0+sfIc0Z6HcWIOA=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
