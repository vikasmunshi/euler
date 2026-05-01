#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 230: Fibonacci Words.

Problem Statement:
    For any two strings of digits, A and B, we define F_{A,B} to be the sequence
    (A, B, AB, BAB, ABBAB, ...) in which each term is the concatenation of the
    previous two.

    Further, we define D_{A,B}(n) to be the nth digit in the first term of F_{A,B}
    that contains at least n digits.

    Example:
    Let A = 1415926535, B = 8979323846. We wish to find D_{A,B}(35), say.
    The first few terms of F_{A,B} are:
    1415926535
    8979323846
    14159265358979323846
    897932384614159265358979323846
    14159265358979323846897932384614159265358979323846
    Then D_{A,B}(35) is the 35th digit in the fifth term, which is 9.

    Now we use for A the first 100 digits of pi behind the decimal point:
    14159265358979323846264338327950288419716939937510
    58209749445923078164062862089986280348253421170679

    and for B the next hundred digits:
    82148086513282306647093844609550582231725359408128
    48111745028410270193852110555964462294895493038196

    Find sum_{n = 0}^{17} 10^n * D_{A,B}((127 + 19 n) * 7^n).

URL: https://projecteuler.net/problem=230
"""
from typing import Any

euler_problem: int = 230
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
