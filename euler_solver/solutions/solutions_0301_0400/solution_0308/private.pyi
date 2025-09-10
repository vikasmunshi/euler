#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 308: An Amazing Prime-generating Automaton.

Problem Statement:
    A program written in the programming language Fractran consists of a list of
    fractions.

    The internal state of the Fractran Virtual Machine is a positive integer,
    which is initially set to a seed value. Each iteration of a Fractran
    program multiplies the state integer by the first fraction in the list
    which will leave it an integer.

    For example, one of the Fractran programs that John Horton Conway wrote for
    prime-generation consists of the following 14 fractions:
    17/91, 78/85, 19/51, 23/38, 29/33, 77/29, 95/23, 77/19, 1/17, 11/13,
    13/11, 15/2, 1/7, 55/1

    Starting with the seed integer 2, successive iterations of the program
    produce the sequence:
    15, 825, 725, 1925, 2275, 425, ..., 68, 4, 30, ..., 136, 8, 60, ...,
    544, 32, 240, ...

    The powers of 2 that appear in this sequence are 2^2, 2^3, 2^5, ...
    It can be shown that all the powers of 2 in this sequence have prime
    exponents and that all the primes appear as exponents of powers of 2,
    in proper order!

    If someone uses the above Fractran program to solve Project Euler Problem 7
    (find the 10001st prime), how many iterations would be needed until the
    program produces 2^(10001st prime)?

Solution Approach:
    Simulate the Fractran machine by maintaining the current integer state and
    iteratively multiplying by the first fraction whose numerator times state is
    divisible by its denominator. Represent fractions as reduced integer pairs
    (num, den) and test divisibility via modular arithmetic.
    Optimize by maintaining prime-exponent vectors for the primes appearing in
    numerators and denominators so divisibility and updates are O(k) per step.
    Precompute the target exponent as the n-th prime (use a fast prime sieve).
    The running time is proportional to the number of Fractran iterations
    required; additional acceleration requires pattern detection or state
    compression to skip repeated cycles.

Answer: ...
URL: https://projecteuler.net/problem=308
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 308
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 3}},
    {'category': 'main', 'input': {'n': 10001}},
    {'category': 'extra', 'input': {'n': 20000}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_an_amazing_prime_generating_automaton_p0308_s0(*, n: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))