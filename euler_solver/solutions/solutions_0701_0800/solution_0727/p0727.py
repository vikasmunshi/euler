#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 727: Triangle of Circular Arcs.

Problem Statement:
    Let r_a, r_b and r_c be the radii of three circles that are mutually and externally
    tangent to each other. The three circles then form a triangle of circular arcs
    between their tangency points as shown for the three blue circles in the picture.

    Define the circumcircle of this triangle to be the red circle, with centre D, passing
    through their tangency points. Further define the incircle of this triangle to be the
    green circle, with centre E, that is mutually and externally tangent to all the three
    blue circles. Let d = |DE| be the distance between the centres of the circumcircle
    and the incircle.

    Let E(d) be the expected value of d when r_a, r_b and r_c are integers chosen uniformly
    such that 1 ≤ r_a < r_b < r_c ≤ 100 and gcd(r_a, r_b, r_c) = 1.

    Find E(d), rounded to eight places after the decimal point.

URL: https://projecteuler.net/problem=727
"""
from typing import Any

euler_problem: int = 727
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
