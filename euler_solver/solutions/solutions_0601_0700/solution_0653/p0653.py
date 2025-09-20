#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 653: Frictionless Tube.

Problem Statement:
    Consider a horizontal frictionless tube with length L millimetres, and a diameter
    of 20 millimetres. The east end of the tube is open, while the west end is sealed.
    The tube contains N marbles of diameter 20 millimetres at designated starting
    locations, each one initially moving either westward or eastward with common speed v.

    Since there are marbles moving in opposite directions, there are bound to be some
    collisions. We assume that the collisions are perfectly elastic, so both marbles
    involved instantly change direction and continue with speed v away from the
    collision site. Similarly, if the west-most marble collides with the sealed end
    of the tube, it instantly changes direction and continues eastward at speed v.
    On the other hand, once a marble reaches the unsealed east end, it exits the tube
    and has no further interaction with the remaining marbles.

    To obtain the starting positions and initial directions, we use the pseudo-random
    sequence r_j defined by:
    r_1 = 6563116
    r_(j+1) = r_j^2 mod 32745673

    The west-most marble is initially positioned with a gap of (r_1 mod 1000) + 1
    millimetres between it and the sealed end of the tube, measured from the west-most
    point of the surface of the marble. Then, for 2 ≤ j ≤ N, counting from the west,
    the gap between the (j-1)th and jth marbles, as measured from their closest points,
    is given by (r_j mod 1000) + 1 millimetres. Furthermore, the jth marble is initially
    moving eastward if r_j ≤ 10000000, and westward if r_j > 10000000.

    For example, with N=3, the sequence specifies gaps of 117, 432, and 173 millimetres.
    The marbles' centres are therefore 127, 579, and 772 millimetres from the sealed west
    end of the tube. The west-most marble initially moves eastward, while the other two
    initially move westward.

    Under this setup, and with a five metre tube (L=5000), it turns out that the middle
    (second) marble travels 5519 millimetres before its centre reaches the east-most end
    of the tube.

    Let d(L, N, j) be the distance in millimetres that the jth marble travels before its
    centre reaches the eastern end of the tube. So d(5000, 3, 2) = 5519. You are also
    given that d(10000, 11, 6) = 11780 and d(100000, 101, 51) = 114101.

    Find d(1000000000, 1000001, 500001).

URL: https://projecteuler.net/problem=653
"""
from typing import Any

euler_problem: int = 653
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'L': 5000, 'N': 3, 'j': 2}, 'answer': None},
    {'category': 'dev', 'input': {'L': 10000, 'N': 11, 'j': 6}, 'answer': None},
    {'category': 'dev', 'input': {'L': 100000, 'N': 101, 'j': 51}, 'answer': None},
    {'category': 'main', 'input': {'L': 1000000000, 'N': 1000001, 'j': 500001}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
