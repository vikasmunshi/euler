#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 363: Bézier Curves.

Problem Statement:
    A cubic Bézier curve is defined by four points: P0, P1, P2, and P3.

    The curve is constructed as follows:

    On the segments P0 P1, P1 P2, and P2 P3 the points Q0, Q1, and Q2 are
    drawn such that P0Q0/P0P1 = P1Q1/P1P2 = P2Q2/P2P3 = t, with t in [0, 1].

    On the segments Q0 Q1 and Q1 Q2 the points R0 and R1 are drawn such that
    Q0R0/Q0Q1 = Q1R1/Q1Q2 = t for the same value of t.

    On the segment R0 R1 the point B is drawn such that R0B/R0R1 = t for the
    same value of t.

    The Bézier curve defined by the points P0, P1, P2, P3 is the locus of B as
    Q0 takes all possible positions on the segment P0 P1. (Please note that for
    all points the value of t is the same.)

    From the construction it is clear that the Bézier curve will be tangent to
    the segments P0 P1 in P0 and P2 P3 in P3.

    A cubic Bézier curve with P0 = (1, 0), P1 = (1, v), P2 = (v, 1), and P3 =
    (0, 1) is used to approximate a quarter circle. The value v > 0 is chosen
    such that the area enclosed by the lines OP0, OP3 and the curve is equal to
    pi/4 (the area of the quarter circle).

    By how many percent does the length of the curve differ from the length of
    the quarter circle? That is, if L is the length of the curve, calculate
    100 * (L - pi/2) / (pi/2). Give your answer rounded to 10 digits behind the
    decimal point.

URL: https://projecteuler.net/problem=363
"""
from typing import Any

euler_problem: int = 363
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}, 'answer': None},
]
encrypted: str = (
    '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'
    'Rd+9LbFU+/4H4Xv/70Iiiw=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
