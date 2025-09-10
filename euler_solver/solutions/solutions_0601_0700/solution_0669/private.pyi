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

Solution Approach:
    Use combinatorics and number theory around Fibonacci numbers to constrain seating.
    Model the problem as a circular permutation with adjacency sums in Fibonacci sequence.
    Exploit properties of unique arrangements and indexing in the large-n case.
    Efficiently compute knight number at a given position without full permutation.
    Expected complexity depends on Fibonacci number manipulations and pattern decompositions.

Answer: ...
URL: https://projecteuler.net/problem=669
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 669
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 7, 'position': 3}},
    {'category': 'main', 'input': {'n': 99194853094755497, 'position': 10000000000000000}},
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_the_kings_banquet_p0669_s0(*, n: int, position: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))