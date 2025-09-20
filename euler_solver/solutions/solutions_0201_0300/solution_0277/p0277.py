#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 277: A Modified Collatz Sequence.

Problem Statement:
    A modified Collatz sequence of integers is obtained from a starting value a1
    in the following way:
    a_{n+1} = a_n/3                if a_n is divisible by 3.  Denote this "D".
    a_{n+1} = (4*a_n + 2)/3        if a_n mod 3 = 1.        Denote this "U".
    a_{n+1} = (2*a_n - 1)/3        if a_n mod 3 = 2.        Denote this "d".
    The sequence terminates when some a_n = 1.
    Given any integer, we can list the sequence of steps. For example, for
    a1 = 231 the sequence is {231,77,51,17,11,7,10,14,9,3,1} which corresponds to
    the steps "DdDddUUdDD".
    For a1 = 1004064 the sequence begins with DdDddUUdDD; 1004064 is the
    smallest a1 > 10^6 that begins with that step sequence.
    What is the smallest a1 > 10^15 that begins with the sequence
    "UDDDUdddDDUDDddDdDddDDUDDdUUDd"?

URL: https://projecteuler.net/problem=277
"""
from typing import Any

euler_problem: int = 277
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'steps': 'DdDddUUdDD', 'min_start': 1000000},
     'answer': None},
    {'category': 'main', 'input': {'steps': 'UDDDUdddDDUDDddDdDddDDUDDdUUDd', 'min_start': 1000000000000000},
     'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
