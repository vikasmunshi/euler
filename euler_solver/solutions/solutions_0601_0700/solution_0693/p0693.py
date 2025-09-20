#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 693: Finite Sequence Generator.

Problem Statement:
    Two positive integers x and y (x > y) can generate a sequence in the following
    manner:
        a_x = y is the first term,
        a_{z+1} = a_z^2 mod z for z = x, x+1, x+2, ...
        the generation stops when a term becomes 0 or 1.

    The number of terms in this sequence is denoted l(x,y).

    For example, with x = 5 and y = 3, we get a_5 = 3, a_6 = 3^2 mod 5 = 4, a_7 =
    4^2 mod 6 = 4, etc., giving the sequence of 29 terms:
        3,4,4,2,4,7,9,4,4,3,9,6,4,16,4,16,16,4,16,3,9,6,10,19,25,16,16,8,0
    Hence l(5,3) = 29.

    g(x) is defined to be the maximum value of l(x,y) for y < x. For example, g(5) = 29.

    Further, define f(n) to be the maximum value of g(x) for x <= n. For example,
    f(100) = 145 and f(10000) = 8824.

    Find f(3000000).

URL: https://projecteuler.net/problem=693
"""
from typing import Any

euler_problem: int = 693
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 3000000}, 'answer': None},
]
encrypted: str = (
    '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'
    '/5m7CMUVF+7s4jLRINA8Dw5FvcUHe1SC'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
