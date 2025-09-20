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

URL: https://projecteuler.net/problem=196
"""
from typing import Any

euler_problem: int = 196
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n1': 8, 'n2': 9}, 'answer': None},
    {'category': 'main', 'input': {'n1': 5678027, 'n2': 7208785}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
