#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 541: Divisibility of Harmonic Number Denominators.

Problem Statement:
    The nth harmonic number H_n is defined as the sum of the multiplicative inverses
    of the first n positive integers, and can be written as a reduced fraction a_n/b_n:
    H_n = sum_{k=1}^n 1/k = a_n / b_n with gcd(a_n, b_n) = 1.

    Let M(p) be the largest value of n such that b_n is not divisible by p.

    For example, M(3) = 68 because H_68 = a_68 / b_68, with b_68 not divisible by 3,
    but all larger harmonic numbers have denominators divisible by 3.

    You are given M(7) = 719102.

    Find M(137).

URL: https://projecteuler.net/problem=541
"""
from typing import Any

euler_problem: int = 541
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'p': 3}, 'answer': None},
    {'category': 'main', 'input': {'p': 137}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
