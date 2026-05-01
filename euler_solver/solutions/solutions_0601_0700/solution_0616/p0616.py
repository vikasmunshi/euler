#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 616: Creative Numbers.

Problem Statement:
    Alice plays the following game, she starts with a list of integers L and on each
    step she can either:
        remove two elements a and b from L and add a^b to L
    or conversely remove an element c from L that can be written as a^b, with a and b
    being two integers such that a, b > 1, and add both a and b to L.

    For example starting from the list L={8}, Alice can remove 8 and add 2 and 3
    resulting in L={2,3} in a first step. Then she can obtain L={9} in a second step.

    Note that the same integer is allowed to appear multiple times in the list.

    An integer n > 1 is said to be creative if for any integer m > 1 Alice can obtain
    a list that contains m starting from L={n}.

    Find the sum of all creative integers less than or equal to 10^12.

URL: https://projecteuler.net/problem=616
"""
from typing import Any

euler_problem: int = 616
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
