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

URL: https://projecteuler.net/problem=624
"""
from typing import Any

euler_problem: int = 624
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 2}, 'answer': None},
    {'category': 'dev', 'input': {'n': 3}, 'answer': None},
    {'category': 'main', 'input': {'n': 1000000000000000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
