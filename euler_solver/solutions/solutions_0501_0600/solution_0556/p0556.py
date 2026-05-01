#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 556: Squarefree Gaussian Integers.

Problem Statement:
    A Gaussian integer is a number z = a + bi where a, b are integers and i^2 = -1.
    Gaussian integers are a subset of the complex numbers, and the integers are the subset
    of Gaussian integers for which b = 0.

    A Gaussian integer unit is one for which a^2 + b^2 = 1, i.e. one of 1, i, -1, -i.
    Let's define a proper Gaussian integer as one for which a > 0 and b >= 0.

    A Gaussian integer z_1 = a_1 + b_1 i is said to be divisible by z_2 = a_2 + b_2 i if
    z_3 = a_3 + b_3 i = z_1 / z_2 is a Gaussian integer.
    z_1 is divisible by z_2 if (a_1 a_2 + b_1 b_2) / (a_2^2 + b_2^2) and
    (a_2 b_1 - a_1 b_2) / (a_2^2 + b_2^2) are integers.
    For example, 2 is divisible by 1 + i because 2/(1 + i) = 1 - i is a Gaussian integer.

    A Gaussian prime is a Gaussian integer that is divisible only by a unit, itself, or itself times a unit.
    For example, 1 + 2i is a Gaussian prime because it is only divisible by 1, i, -1, -i,
    1 + 2i, i(1 + 2i) = i - 2, -(1 + 2i) = -1 - 2i and -i(1 + 2i) = 2 - i.
    2 is not a Gaussian prime as it is divisible by 1 + i.

    A Gaussian integer can be uniquely factored as the product of a unit and proper Gaussian primes.
    For example 2 = -i(1 + i)^2 and 1 + 3i = (1 + i)(2 + i).
    A Gaussian integer is said to be squarefree if its prime factorization does not contain
    repeated proper Gaussian primes.
    So 2 is not squarefree over the Gaussian integers, but 1 + 3i is.
    Units and Gaussian primes are squarefree by definition.

    Let f(n) be the count of proper squarefree Gaussian integers with a^2 + b^2 <= n.
    For example f(10) = 7 because 1, 1 + i, 1 + 2i, 1 + 3i = (1 + i)(2 + i), 2 + i, 3 and
    3 + i = -i(1 + i)(1 + 2i) are squarefree, while 2 = -i(1 + i)^2 and 2 + 2i = -i(1 + i)^3
    are not.
    You are given f(10^2) = 54, f(10^4) = 5218 and f(10^8) = 52126906.

    Find f(10^14).

URL: https://projecteuler.net/problem=556
"""
from typing import Any

euler_problem: int = 556
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 100}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 100000000000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
