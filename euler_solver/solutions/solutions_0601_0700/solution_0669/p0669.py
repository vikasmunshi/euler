#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 669: The King's Banquet.

Problem Statement:
    The Knights of the Order of Fibonacci are preparing a grand feast for their king.
    There are n knights, and each knight is assigned a distinct number from 1 to n.

    When the knights sit down at the roundtable for their feast, they follow a peculiar
    seating rule: two knights can only sit next to each other if their respective numbers
    sum to a Fibonacci number.

    When the n knights all try to sit down around a circular table with n chairs, they
    are unable to find a suitable seating arrangement for any n>2 despite their best
    efforts. Just when they are about to give up, they remember that the king will sit
    on his throne at the table as well.

    Suppose there are n=7 knights and 7 chairs at the roundtable, in addition to the king’s
    throne. After some trial and error, they come up with the following seating arrangement
    (K represents the king):

        The sums 4+1, 1+7, 7+6, 6+2, 2+3, and 3+5 are all Fibonacci numbers.

    It should also be mentioned that the king always prefers an arrangement where the knight
    to his left has a smaller number than the knight to his right. With this additional
    rule, the above arrangement is unique for n=7, and the knight sitting in the 3rd chair
    from the king’s left is knight number 7.

    Later, several new knights are appointed to the Order, giving 34 knights and chairs in
    addition to the king's throne. The knights eventually determine that there is a unique
    seating arrangement for n=34 satisfying the above rules, and this time knight number 30
    is sitting in the 3rd chair from the king's left.

    Now suppose there are n=99194853094755497 knights and the same number of chairs at the
    roundtable (not including the king’s throne). After great trials and tribulations, they
    are finally able to find the unique seating arrangement for this value of n that satisfies
    the above rules.

    Find the number of the knight sitting in the 10000000000000000th chair from the king’s left.

URL: https://projecteuler.net/problem=669
"""
from typing import Any

euler_problem: int = 669
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 7, 'position': 3}, 'answer': None},
    {'category': 'main', 'input': {'n': 99194853094755497, 'position': 10000000000000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
