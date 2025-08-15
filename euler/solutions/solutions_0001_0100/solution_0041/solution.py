#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 41: Pandigital Prime.

Problem Statement:
    We shall say that an n-digit number is pandigital if it makes use of all the digits
    1 to n exactly once. For example, 2143 is a 4-digit pandigital and is also prime.

    What is the largest n-digit pandigital prime that exists?

Solution Approach:
    Use combinatorics to generate pandigital numbers for n from 9 down to 1.
    Check for primality efficiently using a fast primality test.
    Exploit the divisibility rule of sum digits to eliminate certain n quickly.
    Expect a backtrack or permutations approach combined with primality test.
    Time complexity depends on permutations of digits (factorial n) with primality checks.

Answer: 7652413
URL: https://projecteuler.net/problem=41
"""
from __future__ import annotations

from typing import Any

from euler.logger import logger
from euler.maths.pandigital_numbers import gen_n_digit_pandigital_numbers
from euler.maths.primes import is_prime
from euler.setup import evaluate, register_solution

euler_problem: int = 41
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}}
]


@register_solution(euler_problem=euler_problem, test_cases=test_cases[:])
def solve_pandigital_prime_p0041_s0() -> int:
    pandigital_primes = (number
                         for length in (7, 4)
                         for number in (gen_n_digit_pandigital_numbers(length, descending=True))
                         if is_prime(number))
    return next(pandigital_primes)


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))
