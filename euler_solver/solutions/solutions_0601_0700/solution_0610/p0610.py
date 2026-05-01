#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 610: Roman Numerals II.

Problem Statement:
    A random generator produces a sequence of symbols drawn from the set
    {I, V, X, L, C, D, M, #}. Each item in the sequence is determined by
    selecting one of these symbols at random, independently of the other items
    in the sequence. At each step, the seven letters are equally likely to be
    selected, with probability 14% each, but the # symbol only has a 2% chance
    of selection.

    We write down the sequence of letters from left to right as they are
    generated, and we stop at the first occurrence of the # symbol (without
    writing it). However, we stipulate that what we have written down must
    always (when non-empty) be a valid Roman numeral representation in
    minimal form. If appending the next letter would contravene this then we
    simply skip it and try again with the next symbol generated.

    Please take careful note of About... Roman Numerals for the definitive rules
    for this problem on what constitutes a "valid Roman numeral
    representation" and "minimal form". For example, the (only) sequence that
    represents 49 is XLIX. The subtractive combination IL is invalid because
    of rule (ii), while XXXXIX is valid but not minimal. The rules do not place
    any restriction on the number of occurrences of M, so all positive integers
    have a valid representation. These are the same rules as were used in
    Problem 89, and members are invited to solve that problem first.

    Find the expected value of the number represented by what we have written
    down when we stop. (If nothing is written down then count that as zero.)
    Give your answer rounded to 8 places after the decimal point.

URL: https://projecteuler.net/problem=610
"""
from typing import Any

euler_problem: int = 610
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
