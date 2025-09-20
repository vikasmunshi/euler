#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 674: Solving I-equations.

Problem Statement:
    We define the I operator as the function
        I(x,y) = (1+x+y)^2 + y - x
    and I-expressions as arithmetic expressions built only from variable names and applications
    of I. A variable name may consist of one or more letters. For example, the three expressions
    x, I(x,y), and I(I(x,ab),x) are all I-expressions.

    For two I-expressions e1 and e2 such that the equation e1 = e2 has a solution in non-negative
    integers, we define the least simultaneous value of e1 and e2 to be the minimum value taken
    by e1 and e2 on such a solution. If the equation e1 = e2 has no solution in non-negative
    integers, we define the least simultaneous value of e1 and e2 to be 0. For example,
    consider the following three I-expressions:
        A = I(x, I(z,t))
        B = I(I(y,z), y)
        C = I(I(x,z), y)
    The least simultaneous value of A and B is 23, attained for x=3,y=1,z=t=0. On the other hand,
    A = C has no solutions in non-negative integers, so the least simultaneous value of A and C
    is 0. The total sum of least simultaneous pairs made of I-expressions from {A,B,C} is 26.

    Find the sum of least simultaneous values of all I-expression pairs made of distinct
    expressions from file I-expressions.txt (pairs (e1, e2) and (e2, e1) are considered
    to be identical). Give the last nine digits of the result as the answer.

URL: https://projecteuler.net/problem=674
"""
from typing import Any

euler_problem: int = 674
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}, 'answer': None},
]
encrypted: str = (
    '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'
    'Eib/w9Acno2HlvBCIXp/PcIshXs='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
