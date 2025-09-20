#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 790: Clock Grid.

Problem Statement:
    There is a grid of length and width 50515093 points. A clock is placed on each grid
    point. The clocks are all analogue showing a single hour hand initially pointing at 12.

    A sequence S_t is created where:
        S_0 = 290797
        S_t = S_{t-1}^2 mod 50515093 for t > 0

    The four numbers N_t = (S_{4t-4}, S_{4t-3}, S_{4t-2}, S_{4t-1}) represent a range within
    the grid, with the first pair representing the x-bounds and the second pair the y-bounds.
    For example, if N_t = (3,9,47,20), the range would be 3 ≤ x ≤ 9 and 20 ≤ y ≤ 47, which
    includes 196 clocks.

    For each t > 0, the clocks within the range represented by N_t are moved to the next hour
    (12 → 1 → 2 → ...).

    Define C(t) to be the sum of the hours that the clock hands are pointing to after timestep t.
    Given: C(0) = 30621295449583788, C(1) = 30613048345941659, C(10) = 21808930308198471,
    and C(100) = 16190667393984172.

    Find C(10^5).

URL: https://projecteuler.net/problem=790
"""
from typing import Any

euler_problem: int = 790
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'timesteps': 10}, 'answer': None},
    {'category': 'main', 'input': {'timesteps': 100000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
