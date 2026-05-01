#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 126: Cuboid Layers.

Problem Statement:
    The minimum number of cubes to cover every visible face on a cuboid
    measuring 3 x 2 x 1 is twenty-two.

    If we then add a second layer to this solid it would require forty-six
    cubes to cover every visible face, the third layer would require seventy-
    eight cubes, and the fourth layer would require one-hundred and eighteen
    cubes to cover every visible face.

    However, the first layer on a cuboid measuring 5 x 1 x 1 also requires
    twenty-two cubes; similarly the first layer on cuboids measuring 5 x 3 x 1,
    7 x 2 x 1, and 11 x 1 x 1 all contain forty-six cubes.

    We shall define C(n) to represent the number of cuboids that contain n
    cubes in one of its layers. So C(22) = 2, C(46) = 4, C(78) = 5, and
    C(118) = 8.

    It turns out that 154 is the least value of n for which C(n) = 10.

    Find the least value of n for which C(n) = 1000.

URL: https://projecteuler.net/problem=126
"""
from typing import Any

euler_problem: int = 126
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'target_count': 10}, 'answer': None},
    {'category': 'main', 'input': {'target_count': 1000}, 'answer': None},
    {'category': 'extra', 'input': {'target_count': 2000}, 'answer': None},
]
encrypted: str = (
    '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'
    'mha6IHRA40k66hgMnMYECZB/X+7EQknY'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
