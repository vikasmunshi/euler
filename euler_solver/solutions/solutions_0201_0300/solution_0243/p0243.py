#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 243: Resilience.

Problem Statement:
    A positive fraction whose numerator is less than its denominator is called
    a proper fraction. For any denominator, d, there will be d - 1 proper
    fractions; for example, with d = 12: 1/12, 2/12, 3/12, 4/12, 5/12, 6/12,
    7/12, 8/12, 9/12, 10/12, 11/12.

    We shall call a fraction that cannot be cancelled down a resilient fraction.
    Furthermore we shall define the resilience of a denominator, R(d), to be
    the ratio of its proper fractions that are resilient; for example,
    R(12) = 4/11. In fact, d = 12 is the smallest denominator having a
    resilience R(d) < 4/10.

    Find the smallest denominator d, having a resilience R(d) < 15499/94744.

URL: https://projecteuler.net/problem=243
"""
from typing import Any

euler_problem: int = 243
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'threshold_numer': 4, 'threshold_denom': 10}, 'answer': None},
    {'category': 'main', 'input': {'threshold_numer': 15499, 'threshold_denom': 94744}, 'answer': None},
]
encrypted: str = (
    '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'
    '+S+VBzDtIxCFDu7zKUSMdwORTmBsl1ud'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
