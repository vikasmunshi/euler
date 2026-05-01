#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 646: Bounded Divisors.

Problem Statement:
    Let n be a natural number and p_1^{alpha_1} * p_2^{alpha_2} * ... * p_k^{alpha_k} its prime
    factorisation.
    Define the Liouville function lambda(n) as lambda(n) = (-1)^{sum of alpha_i}.
    (i.e. -1 if the sum of the exponents alpha_i is odd and 1 if the sum is even.)
    Let S(n, L, H) be the sum of lambda(d) * d over all divisors d of n for which L <= d <= H.

    You are given:
      S(10!, 100, 1000) = 1457
      S(15!, 10^3, 10^5) = -107974
      S(30!, 10^8, 10^{12}) = 9766732243224.

    Find S(70!, 10^{20}, 10^{60}) modulo 1000000007.

URL: https://projecteuler.net/problem=646
"""
from typing import Any

euler_problem: int = 646
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 10,
                                  'L': 100,
                                  'H': 1000},
     'answer': None},
    {'category': 'main', 'input': {'n': 70,
                                   'L': 100000000000000000000,
                                   'H': 1000000000000000000000000000000000000000000000000000000000000},
     'answer': None},
    {'category': 'extra', 'input': {'n': 30,
                                    'L': 100000000,
                                    'H': 1000000000000},
     'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
