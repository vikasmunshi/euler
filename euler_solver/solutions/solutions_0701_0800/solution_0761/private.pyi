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

Solution Approach:
    This problem involves geometric pursuit-evasion with optimal strategies.
    Use continuous geometry and optimal control theory to analyze critical speeds.
    Known results for circle and square given; extend reasoning or numerical methods
    for regular hexagon geometry.
    The problem is complex and may involve advanced math or simulations.
    Time complexity depends on the chosen method, likely numerical or analytical.

Answer: ...
URL: https://projecteuler.net/problem=761
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 761
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_runner_and_swimmer_p0761_s0() -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))