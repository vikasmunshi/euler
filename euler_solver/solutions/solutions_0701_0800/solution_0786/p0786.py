#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 786: Billiard.

Problem Statement:
    The following diagram shows a billiard table of a special quadrilateral shape.
    The four angles A, B, C, D are 120 degrees, 90 degrees, 60 degrees, 90 degrees
    respectively, and the lengths AB and AD are equal.

    The diagram on the left shows the trace of an infinitesimally small billiard ball,
    departing from point A, bouncing twice on the edges of the table, and finally
    returning back to point A. The diagram on the right shows another such trace,
    but this time bouncing eight times:

    The table has no friction and all bounces are perfect elastic collisions.
    Note that no bounce should happen on any of the corners, as the behaviour would
    be unpredictable.

    Let B(N) be the number of possible traces of the ball, departing from point A,
    bouncing at most N times on the edges and returning back to point A.

    For example, B(10) = 6, B(100) = 478, B(1000) = 45790.

    Find B(10^9).

URL: https://projecteuler.net/problem=786
"""
from typing import Any

euler_problem: int = 786
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_bounces': 10}, 'answer': None},
    {'category': 'main', 'input': {'max_bounces': 1000000000}, 'answer': None},
    {'category': 'extra', 'input': {'max_bounces': 10000000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'T/dr96eDMr2cT9ETgcrU9A=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
