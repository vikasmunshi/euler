#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 55: Lychrel Numbers.

Problem Statement:
    If we take 47, reverse and add, 47 + 74 = 121, which is palindromic.

    Not all numbers produce palindromes so quickly. For example,
    349 + 943 = 1292
    1292 + 2921 = 4213
    4213 + 3124 = 7337
    That is, 349 took three iterations to arrive at a palindrome.

    Although no one has proved it yet, it is thought that some numbers, like 196,
    never produce a palindrome. A number that never forms a palindrome through
    the reverse and add process is called a Lychrel number. Due to the theoretical
    nature of these numbers, and for the purpose of this problem, we shall assume
    that a number is Lychrel until proven otherwise. In addition you are given that
    for every number below ten-thousand, it will either (i) become a palindrome
    in less than fifty iterations, or, (ii) no one, with all the computing power
    that exists, has managed so far to map it to a palindrome. In fact, 10677 is
    the first number to be shown to require over fifty iterations before producing
    a palindrome: 4668731596684224866951378664 (53 iterations, 28-digits).

    Surprisingly, there are palindromic numbers that are themselves Lychrel numbers;
    the first example is 4994.

    How many Lychrel numbers are there below ten-thousand?

Solution Approach:
    Implement the reverse-and-add process iteratively and check for palindromes.
    Use a limit of 50 iterations as per the problem statement.
    Count numbers below ten-thousand that do not form palindromes within the limit.
    Utilize string reversal or arithmetic to check palindromes efficiently.
    Time complexity is O(N*I*D) where N=10000, I=50 iterations, D=digits to check,
    which is practical for this problem.

Answer: 249
URL: https://projecteuler.net/problem=55
"""
from __future__ import annotations

from typing import Any

from euler_solver.framework import evaluate, logger, register_solution

euler_problem: int = 55
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'max_iterations': 50, 'max_limit': 10000}, 'answer': 249},
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_lychrel_numbers_p0055_s0(*, max_iterations: int, max_limit: int) -> int:
    return sum((is_lychrel(number=i, max_iterations=max_iterations) for i in range(1, max_limit + 1)))


def is_lychrel(*, number: int, max_iterations: int) -> bool:
    for _ in range(max_iterations):
        number += int(str(number)[::-1])
        if str(number) == str(number)[::-1]:
            return False
    else:
        return True


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
