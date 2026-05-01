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

URL: https://projecteuler.net/problem=308
"""
from typing import Any

euler_problem: int = 308
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 3}, 'answer': None},
    {'category': 'main', 'input': {'n': 10001}, 'answer': None},
    {'category': 'extra', 'input': {'n': 20000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
