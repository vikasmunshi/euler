#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 624: Two Heads Are Better Than One.

Problem Statement:
    An unbiased coin is tossed repeatedly until two consecutive heads are obtained.
    Suppose these occur on the (M-1)th and Mth toss.
    Let P(n) be the probability that M is divisible by n.
    For example, the outcomes HH, HTHH, and THTTHH all count towards P(2),
    but THH and HTTHH do not.

    You are given that P(2) = 3/5 and P(3) = 9/31.
    Indeed, it can be shown that P(n) is always a rational number.

    For a prime p and a fully reduced fraction a/b, define Q(a/b, p) to be
    the smallest positive q for which a ≡ bq (mod p).
    For example Q(P(2), 109) = Q(3/5, 109) = 66, because 5·66 = 330 ≡ 3 (mod 109)
    and 66 is the smallest positive such number.
    Similarly Q(P(3), 109) = 46.

    Find Q(P(10^18), 1000000009).

Solution Approach:
    Use probability theory and Markov chains to model the coin tosses and derive
    P(n) rational forms.
    Employ number theory and modular arithmetic to find Q(a/b, p).
    Likely requires fast exponentiation and modular inverses for primes.
    Efficient handling needed for very large n = 10^18.
    Time complexity depends on clever mathematical simplifications.

Answer: ...
URL: https://projecteuler.net/problem=624
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 624
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 2}},
    {'category': 'dev', 'input': {'n': 3}},
    {'category': 'main', 'input': {'n': 10**18}},
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_two_heads_are_better_than_one_p0624_s0(*, n: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))
