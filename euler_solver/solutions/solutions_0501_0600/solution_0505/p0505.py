#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 505: Bidirectional Recurrence.

Problem Statement:
    Let:

        x(0)=0
        x(1)=1
        x(2k)=(3x(k)+2x(floor(k/2))) mod 2^60 for k>=1, where floor is the floor function
        x(2k+1)=(2x(k)+3x(floor(k/2))) mod 2^60 for k>=1
        y_n(k)=
            x(k) if k >= n
            2^60 - 1 - max(y_n(2k), y_n(2k+1)) if k < n
        A(n)=y_n(1)

    You are given:

        x(2)=3
        x(3)=2
        x(4)=11
        y_4(4)=11
        y_4(3)=2^60 - 9
        y_4(2)=2^60 - 12
        y_4(1)=A(4)=8
        A(10)=2^60 - 34
        A(10^3)=101881

    Find A(10^12).

URL: https://projecteuler.net/problem=505
"""
from typing import Any

euler_problem: int = 505
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'n': 1000000000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
