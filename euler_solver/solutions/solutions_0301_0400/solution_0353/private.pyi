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

Solution Approach:
    Model stations as integer lattice points on the sphere of radius r.
    Build a graph where edges connect stations by great-circle arcs; edge risk
    = (arc_length/(pi*r))^2 = (theta/pi)^2 with cos(theta) from normalized dot.
    Enumerate lattice points using representations as sums of three squares.
    Compute shortest-path (minimal total risk) from North to South via Dijkstra
    or a suitable priority-search; exploit symmetry and pruning to reduce nodes.
    Complexity: V = number of lattice points on C(r); Dijkstra O(E log V) with
    careful edge generation and caching should be targeted.

Answer: ...
URL: https://projecteuler.net/problem=353
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 353
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_n': 3}},
    {'category': 'main', 'input': {'max_n': 15}},
    {'category': 'extra', 'input': {'max_n': 20}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_risky_moon_p0353_s0(*, max_n: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))