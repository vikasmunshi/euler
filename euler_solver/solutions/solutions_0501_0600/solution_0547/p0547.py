#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 547: Distance of Random Points Within Hollow Square Laminae.

Problem Statement:
    Assuming that two points are chosen randomly (with uniform distribution) within a
    rectangle, it is possible to determine the expected value of the distance between
    these two points.

    For example, the expected distance between two random points in a unit square is
    about 0.521405, while the expected distance between two random points in a
    rectangle with side lengths 2 and 3 is about 1.317067.

    Now we define a hollow square lamina of size n to be an integer sized square with
    side length n ≥ 3 consisting of n^2 unit squares from which a rectangle consisting
    of x × y unit squares (1 ≤ x,y ≤ n - 2) within the original square has been removed.

    For n = 3 there exists only one hollow square lamina:

    [Illustration of one hollow square lamina for n=3]

    For n = 4 you can find 9 distinct hollow square laminae, allowing shapes to
    reappear in rotated or mirrored form:

    [Illustration of nine hollow square laminae for n=4]

    Let S(n) be the sum of the expected distance between two points chosen randomly
    within each of the possible hollow square laminae of size n. The two points have
    to lie within the area left after removing the inner rectangle, i.e. the gray-colored
    areas in the illustrations above.

    For example, S(3) = 1.6514 and S(4) = 19.6564, rounded to four digits after the
    decimal point.

    Find S(40) rounded to four digits after the decimal point.

URL: https://projecteuler.net/problem=547
"""
from typing import Any

euler_problem: int = 547
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 3}, 'answer': None},
    {'category': 'main', 'input': {'n': 40}, 'answer': None},
    {'category': 'extra', 'input': {'n': 50}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
