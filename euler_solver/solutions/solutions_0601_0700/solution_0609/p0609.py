#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 609: π Sequences.

Problem Statement:
    For every n ≥ 1 the prime-counting function π(n) is equal to the number of primes
    not exceeding n.
    E.g. π(6)=3 and π(100)=25.

    We say that a sequence of integers u = (u_0, ..., u_m) is a π sequence if
        1. u_n ≥ 1 for every n,
        2. u_{n+1} = π(u_n),
        3. u has two or more elements.

    For u_0=10 there are three distinct π sequences: (10,4), (10,4,2) and (10,4,2,1).

    Let c(u) be the number of elements of u that are not prime.
    Let p(n,k) be the number of π sequences u for which u_0 ≤ n and c(u) = k.
    Let P(n) be the product of all p(n,k) that are larger than 0.
    You are given: P(10)=3 × 8 × 9 × 3=648 and P(100)=31038676032.

    Find P(10^8). Give your answer modulo 1000000007.

URL: https://projecteuler.net/problem=609
"""
from typing import Any

euler_problem: int = 609
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 100000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
