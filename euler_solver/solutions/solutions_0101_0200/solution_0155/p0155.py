#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 155: Counting Capacitor Circuits.

Problem Statement:
    An electric circuit uses exclusively identical capacitors of the same
    value C. The capacitors can be connected in series or in parallel to
    form sub-units, which can then be connected in series or in parallel with
    other capacitors or other sub-units to form larger sub-units, and so on
    up to a final circuit.

    Using this simple procedure and up to n identical capacitors, we can
    make circuits having a range of different total capacitances. For
    example, using up to n = 3 capacitors of equal value, we obtain 7
    distinct total capacitance values. If D(n) denotes the number of distinct
    total capacitances obtainable using up to n equal capacitors, we have:
    D(1) = 1, D(2) = 3, D(3) = 7, ...

    Find D(18).

    Reminder: For parallel connections, the total capacitance is
    CT = C1 + C2 + ... . For series connections, 1/CT = 1/C1 + 1/C2 + ...

URL: https://projecteuler.net/problem=155
"""
from typing import Any

euler_problem: int = 155
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 3}, 'answer': None},
    {'category': 'main', 'input': {'n': 18}, 'answer': None},
    {'category': 'extra', 'input': {'n': 20}, 'answer': None},
]
encrypted: str = (
    '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'
    'P0wcVw=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
