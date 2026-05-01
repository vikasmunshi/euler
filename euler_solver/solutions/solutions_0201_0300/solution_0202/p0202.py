#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 202: Laserbeam.

Problem Statement:
    Three mirrors are arranged in the shape of an equilateral triangle, with
    their reflective surfaces pointing inwards. There is an infinitesimal gap
    at each vertex of the triangle through which a laser beam may pass.

    Label the vertices A, B and C. There are 2 ways in which a laser beam may
    enter vertex C, bounce off 11 surfaces, then exit through the same vertex:
    one way is shown below; the other is the reverse of that.

    There are 80840 ways in which a laser beam may enter vertex C, bounce off
    1000001 surfaces, then exit through the same vertex.

    In how many ways can a laser beam enter at vertex C, bounce off
    12017639147 surfaces, then exit through the same vertex?

URL: https://projecteuler.net/problem=202
"""
from typing import Any

euler_problem: int = 202
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'bounces': 11}, 'answer': None},
    {'category': 'main', 'input': {'bounces': 12017639147}, 'answer': None},
    {'category': 'extra', 'input': {'bounces': 1000001}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
