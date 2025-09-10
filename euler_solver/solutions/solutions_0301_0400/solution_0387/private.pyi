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

Solution Approach:
    Generate right-truncatable Harshad numbers by recursion: start from 1..9 and
    append digits, tracking digit sums and divisibility. For each generated
    Harshad number n check if n / sum_digits(n) is prime (strong Harshad).
    For each strong, right-truncatable Harshad n, test candidates p = n*10 + d
    (d in 1..9) for primality and sum those below the limit. Use a fast
    deterministic Miller–Rabin for numbers < 10^14. Time is roughly number of
    generated nodes times small constant for primality tests; memory is small.

Answer: ...
URL: https://projecteuler.net/problem=387
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 387
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10000}},
    {'category': 'main', 'input': {'max_limit': 100000000000000}},
    {'category': 'extra', 'input': {'max_limit': 1000000000000}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_harshad_numbers_p0387_s0(*, max_limit: int) -> int: ...


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))