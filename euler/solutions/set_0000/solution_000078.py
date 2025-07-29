#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r""" Solution to Project Euler problem 78: coin_partitions

Problem Statement:
  Let p(n) represent the number of different ways in which n coins can be
  separated into piles. For example, five coins can be separated into piles in
  exactly seven different ways, so p(5)=7.  OOOOO OOOO   O OOO   OO OOO   O   O
  OO   OO   O OO   O   O   O O   O   O   O   O  Find the least value of n for
  which p(n) is divisible by one million.

Solution Approach:
  Document the mathematical approach here.

URL: https://projecteuler.net/problem=78
Answer: None
"""
from __future__ import annotations

from itertools import count

from euler.evaluator import evaluate_solutions, register_solution
from euler.maths.integer_partitions import num_partitions
from euler.setup import TestCase

test_cases: list[TestCase] = [
    TestCase(
        answer=449,
        is_main_case=False,
        kwargs={'divisor': 1000},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=55374,
        is_main_case=False,
        kwargs={'divisor': 1000000},
        solution_execution_time=None,
        solved=False
    ),
]


# Register this function as a solution for problem #78
@register_solution(problem_number=78, test_cases=test_cases)
def coin_partitions(*, divisor: int) -> int:
    for n in count(2):
        if num_partitions(number=n) % divisor == 0:
            return n
    return -1


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(78))
