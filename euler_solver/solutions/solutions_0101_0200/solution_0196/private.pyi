#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 196: Prime Triplets.

Problem Statement:
    Build a triangle from all positive integers in the following way:

    1
    2 3
    4 5 6
    7 8 9 10
    11 12 13 14 15
    16 17 18 19 20 21
    22 23 24 25 26 27 28
    29 30 31 32 33 34 35 36
    37 38 39 40 41 42 43 44 45
    46 47 48 49 50 51 52 53 54 55
    56 57 58 59 60 61 62 63 64 65 66
    ...

    Each positive integer has up to eight neighbours in the triangle.

    A set of three primes is called a prime triplet if one of the three primes
    has the other two as neighbours in the triangle.

    For example, in the second row, the prime numbers 2 and 3 are elements of
    some prime triplet.

    If row 8 is considered, it contains two primes which are elements of some
    prime triplet, i.e. 29 and 31.
    If row 9 is considered, it contains only one prime which is an element of
    some prime triplet: 37.

    Define S(n) as the sum of the primes in row n which are elements of any
    prime triplet.
    Then S(8)=60 and S(9)=37.

    You are given that S(10000)=950007619.

    Find S(5678027) + S(7208785).

Solution Approach:
    Map positions to values using triangular numbers T_r = r*(r+1)/2; row r holds
    values T_{r-1}+1 ... T_r. Derive closed-form neighbour indices for an entry
    (row, offset) so neighbour values are linear functions of row/offset.
    Generate candidates only in the target rows and test primality of each value.
    Use a fast deterministic Miller–Rabin for 64-bit ranges and a small prime
    sieve for trial division to speed rejection. Count neighbours that are
    prime to identify triplet membership and sum those primes.
    Expected approach: number theory + primality testing; time ~O(r * cost_primality).

Answer: ...
URL: https://projecteuler.net/problem=196
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 196
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n1': 8, 'n2': 9}},
    {'category': 'main', 'input': {'n1': 5678027, 'n2': 7208785}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_prime_triplets_p0196_s0(*, n1: int, n2: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))