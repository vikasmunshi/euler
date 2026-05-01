#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 723: Pythagorean Quadrilaterals.

Problem Statement:
    A pythagorean triangle with catheti a and b and hypotenuse c is
    characterized by the well-known equation a^2+b^2=c^2. However, this can
    also be formulated differently:
    When inscribed into a circle with radius r, a triangle with sides a, b
    and c is pythagorean, if and only if a^2+b^2+c^2=8 r^2.

    Analogously, we call a quadrilateral ABCD with sides a, b, c and d,
    inscribed in a circle with radius r, a pythagorean quadrilateral, if
    a^2+b^2+c^2+d^2=8 r^2.
    We further call a pythagorean quadrilateral a pythagorean lattice grid
    quadrilateral, if all four vertices are lattice grid points with the same
    distance r from the origin O (which then happens to be the centre of the
    circumcircle).

    Let f(r) be the number of different pythagorean lattice grid quadrilaterals
    for which the radius of the circumcircle is r. For example f(1)=1,
    f(sqrt 2)=1, f(sqrt 5)=38 and f(5)=167.
    Two of the pythagorean lattice grid quadrilaterals with r=sqrt 5 are
    illustrated below.

    Let S(n)=sum over d dividing n of f(sqrt d). For example,
    S(325)=S(5^2 * 13)=f(1)+f(sqrt 5)+f(5)+f(sqrt{13})+f(sqrt{65})+f(5 sqrt{13})=2370
    and S(1105)=S(5 * 13 * 17)=5535.

    Find S(1411033124176203125)=S(5^6 * 13^3 * 17^2 * 29 * 37 * 41 * 53 * 61).

URL: https://projecteuler.net/problem=723
"""
from typing import Any

euler_problem: int = 723
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
