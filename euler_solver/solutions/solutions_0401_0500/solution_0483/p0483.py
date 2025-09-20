#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 483: Repeated Permutation.

Problem Statement:
    We define a permutation as an operation that rearranges the order of the elements
    {1, 2, 3, ..., n}. There are n! such permutations, one of which leaves the elements
    in their initial order.

    For n = 3 we have 3! = 6 permutations:
        P1 = keep the initial order
        P2 = exchange the 1st and 2nd elements
        P3 = exchange the 1st and 3rd elements
        P4 = exchange the 2nd and 3rd elements
        P5 = rotate the elements to the right
        P6 = rotate the elements to the left

    If we select one of these permutations and re-apply the same permutation repeatedly,
    we eventually restore the initial order. For a permutation Pi, let f(Pi) be the
    number of steps required to restore the initial order by applying Pi repeatedly.
    For n = 3, we have:
        f(P1) = 1: (1,2,3) -> (1,2,3)
        f(P2) = 2: (1,2,3) -> (2,1,3) -> (1,2,3)
        f(P3) = 2: (1,2,3) -> (3,2,1) -> (1,2,3)
        f(P4) = 2: (1,2,3) -> (1,3,2) -> (1,2,3)
        f(P5) = 3: (1,2,3) -> (3,1,2) -> (2,3,1) -> (1,2,3)
        f(P6) = 3: (1,2,3) -> (2,3,1) -> (3,1,2) -> (1,2,3)

    Let g(n) be the average value of f^2(Pi) over all permutations Pi of length n.
    Example values:
        g(3) = (1^2 + 2^2 + 2^2 + 2^2 + 3^2 + 3^2) / 3! = 31/6 ≈ 5.166666667e0
        g(5) = 2081/120 ≈ 1.734166667e1
        g(20) = 12422728886023769167301/2432902008176640000 ≈ 5.106136147e3

    Find g(350) and write the answer in scientific notation rounded to 10 significant
    digits, using a lowercase e to separate mantissa and exponent, as in the examples.

URL: https://projecteuler.net/problem=483
"""
from typing import Any

euler_problem: int = 483
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'n': 350}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
