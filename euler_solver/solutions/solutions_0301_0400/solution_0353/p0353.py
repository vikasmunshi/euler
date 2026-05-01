#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 353: Risky Moon.

Problem Statement:
    A moon could be described by the sphere C(r) with centre (0,0,0) and radius r.
    There are stations on the moon at the points on the surface of C(r) with
    integer coordinates. The station at (0,0,r) is called North Pole station,
    the station at (0,0,-r) is called South Pole station.
    All stations are connected with each other via the shortest road on the
    great arc through the stations. A journey between two stations is risky.
    If d is the length of the road between two stations, (d/(pi r))^2 is a
    measure for the risk of the journey (let us call it the risk of the road).
    If the journey includes more than two stations, the risk of the journey is
    the sum of risks of the used roads.
    A direct journey from the North Pole station to the South Pole station has
    the length pi r and risk 1. The journey from the North Pole station to the
    South Pole station via (0,r,0) has the same length, but a smaller risk:
    (( (1/2)*pi*r )/( pi*r ))^2 + (( (1/2)*pi*r )/( pi*r ))^2 = 0.5
    The minimal risk of a journey from the North Pole station to the South Pole
    station on C(r) is M(r).
    You are given that M(7)=0.1784943998 rounded to 10 digits behind the
    decimal point.
    Find sum_{n=1}^{15} M(2^n-1).
    Give your answer rounded to 10 digits behind the decimal point in the
    form a.bcdefghijk.

URL: https://projecteuler.net/problem=353
"""
from typing import Any

euler_problem: int = 353
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_n': 3}, 'answer': None},
    {'category': 'main', 'input': {'max_n': 15}, 'answer': None},
    {'category': 'extra', 'input': {'max_n': 20}, 'answer': None},
]
encrypted: str = (
    '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'
    'X48ISvNWybjnN4XcB0FiDZny+Y4FbC/3'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
