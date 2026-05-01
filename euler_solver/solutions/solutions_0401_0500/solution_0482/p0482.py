#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 482: The Incenter of a Triangle.

Problem Statement:
    ABC is an integer sided triangle with incenter I and perimeter p.
    The segments IA, IB and IC have integral length as well.

    Let L = p + |IA| + |IB| + |IC|.

    Let S(P) = sum L for all such triangles where p <= P. For example, S(10^3) = 3619.

    Find S(10^7).

URL: https://projecteuler.net/problem=482
"""
from typing import Any

euler_problem: int = 482
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'max_limit': 10000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
