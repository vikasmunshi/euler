#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 810: XOR-Primes.

Problem Statement:
    We use x⊕y for the bitwise XOR of x and y.

    Define the XOR-product of x and y, denoted by x⊗y, similar to a long
    multiplication in base 2, except that the intermediate results are XORed
    instead of the usual integer addition.

    For example, 7⊗3 = 9, or in base 2, 111_2 ⊗ 11_2 = 1001_2:
        111_2
      ⊗  11_2
      -------
        111_2
      ⊕ 111_2
      -------
       1001_2

    An XOR-prime is an integer n greater than 1 that is not an XOR-product of
    two integers greater than 1. The above example shows that 9 is not an
    XOR-prime. Similarly, 5 = 3⊗3 is not an XOR-prime. The first few XOR-primes
    are 2, 3, 7, 11, 13, ... and the 10th XOR-prime is 41.

    Find the 5,000,000th XOR-prime.

URL: https://projecteuler.net/problem=810
"""
from typing import Any

euler_problem: int = 810
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'n': 5000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'Ea9/146lD5oNbB2mddtqlmWoRDY8ulsH'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
