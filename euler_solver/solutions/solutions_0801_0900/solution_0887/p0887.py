#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 887: Bounded Binary Search.

Problem Statement:
    Consider the problem of determining a secret number from a set {1, ..., N}
    by repeatedly choosing a number y and asking "Is the secret number greater
    than y?".

    If N=1 then no questions need to be asked. If N=2 then only one question
    needs to be asked. If N=64 then six questions need to be asked. However, in
    the latter case if the secret number is 1 then six questions still need to
    be asked. We want to restrict the number of questions asked for small values.

    Let Q(N, d) be the least number of questions needed for a strategy that
    can find any secret number from the set {1, ..., N} where no more than
    x + d questions are needed to find the secret value x.

    It can be proved that Q(N, 0) = N - 1. You are also given Q(7, 1) = 3 and
    Q(777, 2) = 10.

    Find the sum over d=0 to 7 and N=1 to 7^10 of Q(N, d).

URL: https://projecteuler.net/problem=887
"""
from typing import Any

euler_problem: int = 887
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
