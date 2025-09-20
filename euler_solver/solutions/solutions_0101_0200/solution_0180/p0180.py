#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 180: Golden Triplets.

Problem Statement:
    For any integer n, consider the three functions
    f_{1,n}(x,y,z) = x^{n+1} + y^{n+1} - z^{n+1}
    f_{2,n}(x,y,z) = (xy + yz + zx) * (x^{n-1} + y^{n-1} - z^{n-1})
    f_{3,n}(x,y,z) = xyz * (x^{n-2} + y^{n-2} - z^{n-2})

    and their combination
    f_n(x,y,z) = f_{1,n}(x,y,z) + f_{2,n}(x,y,z) - f_{3,n}(x,y,z).

    We call (x,y,z) a golden triple of order k if x, y, and z are rational
    numbers of the form a/b with 0 < a < b <= k and there is at least one
    integer n such that f_n(x,y,z) = 0.

    Let s(x,y,z) = x + y + z.
    Let t = u/v be the sum of all distinct s(x,y,z) for all golden triples
    (x,y,z) of order 35. All the s(x,y,z) and t must be in reduced form.

    Find u + v.

URL: https://projecteuler.net/problem=180
"""
from typing import Any

euler_problem: int = 180
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 35}, 'answer': None},
    {'category': 'extra', 'input': {'max_limit': 50}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
