#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 256: Tatami-Free Rooms.

Problem Statement:
    Tatami are rectangular mats, used to completely cover the floor of a room,
    without overlap.

    Assuming that the only type of available tatami has dimensions 1 x 2, there
    are limitations for the shapes and sizes of rooms that can be covered.

    We consider only rectangular rooms with integer dimensions a, b and even
    size s = a * b. We use 'size' to denote the floor surface area of the
    room, and without loss of generality require a <= b.

    There is one rule when laying out tatami: there must be no points where
    corners of four different mats meet.

    Because of this rule, certain even-sized rooms cannot be covered with
    tatami: we call them tatami-free rooms. Define T(s) as the number of
    tatami-free rooms of size s.

    The smallest tatami-free room has size s = 70 with dimensions 7 x 10.
    Other rooms of size 70 are 1 x 70, 2 x 35 and 5 x 14, so T(70) = 1.

    Similarly, T(1320) = 5 because the five tatami-free rooms of size 1320
    are 20 x 66, 22 x 60, 24 x 55, 30 x 44 and 33 x 40. In fact 1320 is the
    smallest s for which T(s) = 5.

    Find the smallest room-size s for which T(s) = 200.

URL: https://projecteuler.net/problem=256
"""
from typing import Any

euler_problem: int = 256
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'target_T': 1}, 'answer': None},
    {'category': 'main', 'input': {'target_T': 200}, 'answer': None},
    {'category': 'extra', 'input': {'target_T': 5}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
