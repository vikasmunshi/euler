#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 143: Torricelli Triangles.

Problem Statement:
    Let ABC be a triangle with all interior angles being less than 120 degrees.
    Let X be any point inside the triangle and let XA = p, XC = q, and XB = r.

    Fermat challenged Torricelli to find the position of X such that p + q + r
    was minimised.

    Torricelli proved that if equilateral triangles AOB, BNC and AMC are
    constructed on each side of triangle ABC, the circumscribed circles of AOB,
    BNC and AMC will intersect at a single point, T, inside the triangle. He
    showed that T, called the Torricelli/Fermat point, minimises p + q + r.
    Moreover, when the sum is minimised, AN = BM = CO = p + q + r and AN, BM
    and CO also intersect at T.

    If the sum is minimised and a, b, c, p, q and r are all positive integers
    we shall call triangle ABC a Torricelli triangle. For example, a = 399,
    b = 455, c = 511 is an example of a Torricelli triangle, with
    p + q + r = 784.

    Find the sum of all distinct values of p + q + r <= 120000 for Torricelli
    triangles.

URL: https://projecteuler.net/problem=143
"""
from typing import Any

euler_problem: int = 143
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 1000}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 120000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
