#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 200: Prime-proof Squbes.

Problem Statement:
    We shall define a sqube to be a number of the form, p^2 q^3, where p and q are
    distinct primes. For example, 200 = 5^2 2^3 or 120072949 = 23^2 61^3.

    The first five squbes are 72, 108, 200, 392, and 500.

    Interestingly, 200 is also the first number for which you cannot change any single
    digit to make a prime; we shall call such numbers, prime-proof. The next
    prime-proof sqube which contains the contiguous sub-string "200" is 1992008.

    Find the 200th prime-proof sqube containing the contiguous sub-string "200".

Solution Approach:
    Generate squbes p^2 q^3 with distinct primes p,q in ascending order and test
    each candidate for the substring "200" and for being prime-proof.
    Use a fast prime sieve for generating primes and a Miller-Rabin primality
    test for candidate primes during digit-change checks. Produce numbers in
    increasing order via a priority queue or by bounding p and q and sorting.
    Expected to search through many squbes but stop once the 200th match is found.

Answer: ...
URL: https://projecteuler.net/problem=200
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 200
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 1}},
    {'category': 'main', 'input': {'n': 200}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_prime_proof_squbes_p0200_s0(*, n: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))