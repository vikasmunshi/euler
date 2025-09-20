#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 828: Numbers Challenge.

Problem Statement:
    It is a common recreational problem to make a target number using a selection
    of other numbers. In this problem you will be given six numbers and a target
    number.

    For example, given the six numbers 2, 3, 4, 6, 7, 25, and a target of 211, one
    possible solution is:
    211 = (3+6)*25 − (4*7)/2
    This uses all six numbers. However, it is not necessary to do so. Another
    solution that does not use the 7 is:
    211 = (25−2)*(6+3) + 4

    Define the score of a solution to be the sum of the numbers used. In the above
    example problem, the two given solutions have scores 47 and 40 respectively.
    It turns out that this problem has no solutions with score less than 40.

    When combining numbers, the following rules must be observed:
        Each available number may be used at most once.
        Only the four basic arithmetic operations are permitted: +, -, *, /.
        All intermediate values must be positive integers, so for example (3/2) is
        never permitted as a subexpression (even if the final answer is an integer).

    The attached file number-challenges.txt contains 200 problems, one per line in
    the format:
    211:2,3,4,6,7,25
    where the number before the colon is the target and the remaining comma-separated
    numbers are those available to be used.

    Numbering the problems 1, 2, ..., 200, we let s_n be the minimum score of the
    solution to the nth problem. For example, s_1 = 40, as the first problem in the
    file is the example given above. Note that not all problems have a solution; in
    such cases we take s_n = 0.

    Find sum_{n=1 to 200} 3^n s_n. Give your answer modulo 1005075251.

URL: https://projecteuler.net/problem=828
"""
from typing import Any

euler_problem: int = 828
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'file_url': 'https://projecteuler.net/project/resources/p828_number_challenges.txt'},
     'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
