#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 387: Harshad Numbers.

Problem Statement:
    A Harshad or Niven number is a number that is divisible by the sum of its
    digits. 201 is a Harshad number because it is divisible by 3 (the sum of
    its digits). When we truncate the last digit from 201, we get 20, which is
    a Harshad number. When we truncate the last digit from 20, we get 2, which
    is also a Harshad number. Let's call a Harshad number that, while
    recursively truncating the last digit, always results in a Harshad number a
    right truncatable Harshad number.

    Also: 201/3 = 67 which is prime. Let's call a Harshad number that, when
    divided by the sum of its digits, results in a prime a strong Harshad
    number.

    Now take the number 2011 which is prime. When we truncate the last digit
    from it we get 201, a strong Harshad number that is also right
    truncatable. Let's call such primes strong, right truncatable Harshad
    primes.

    You are given that the sum of the strong, right truncatable Harshad primes
    less than 10000 is 90619.

    Find the sum of the strong, right truncatable Harshad primes less than
    10^14.

URL: https://projecteuler.net/problem=387
"""
from typing import Any

euler_problem: int = 387
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10000}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 100000000000000}, 'answer': None},
    {'category': 'extra', 'input': {'max_limit': 1000000000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
