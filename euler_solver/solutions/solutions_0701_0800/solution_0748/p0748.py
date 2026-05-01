#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 748: Upside Down Diophantine Equation.

Problem Statement:
    Upside Down is a modification of the famous Pythagorean equation:
        1/x^2 + 1/y^2 = 13/z^2.

    A solution (x,y,z) to this equation with x,y and z positive integers is a
    primitive solution if gcd(x,y,z) = 1.

    Let S(N) be the sum of x + y + z over primitive Upside Down solutions such
    that 1 <= x,y,z <= N and x <= y.
    For N=100 the primitive solutions are (2,3,6) and (5,90,18), thus S(10^2)=124.
    It can be checked that S(10^3)=1470 and S(10^5)=2340084.

    Find S(10^16) and give the last 9 digits as your answer.

URL: https://projecteuler.net/problem=748
"""
from typing import Any

euler_problem: int = 748
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 100}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 10000000000000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'fk9M9e3oDLfOwGJ6lHv/sF26MRM='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
