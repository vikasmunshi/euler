#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r""" Solution to Project Euler problem 77: prime_summations

Problem Statement:
  It is possible to write ten as the sum of primes in exactly five different ways:
  \begin{align} &7 + 3\\ &5 + 5\\ &5 + 3 + 2\\ &3 + 3 + 2 + 2\\ &2 + 2 + 2 + 2 + 2
  \end{align} What is the first value which can be written as the sum of primes in
  over five thousand different ways?

Solution Approach:
  Document the mathematical approach here.

URL: https://projecteuler.net/problem=77
Answer: None
"""
from __future__ import annotations

from itertools import count

from euler.evaluator import evaluate_solutions, register_solution
from euler.maths.integer_partitions import get_prime_partitions, num_prime_integer_partitions
from euler.setup import TestCase

test_cases: list[TestCase] = [
    TestCase(
        answer=10,
        is_main_case=False,
        kwargs={'num_prime_partitions': 5},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=25,
        is_main_case=False,
        kwargs={'num_prime_partitions': 50},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=45,
        is_main_case=False,
        kwargs={'num_prime_partitions': 500},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=71,
        is_main_case=False,
        kwargs={'num_prime_partitions': 5000},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=104,
        is_main_case=False,
        kwargs={'num_prime_partitions': 50000},
        solution_execution_time=None,
        solved=False
    ),
]


# Register this function as a solution for problem #77
@register_solution(problem_number=77, test_cases=test_cases)
def sol_1_prime_summations(*, num_prime_partitions: int) -> int:
    for n in count(1):
        if num_prime_integer_partitions(number=n, slots=n) >= num_prime_partitions:
            return n
    return -1


# Register this function as a solution for problem #77
@register_solution(problem_number=77, test_cases=test_cases[:-3])
def sol_2_prime_summations(*, num_prime_partitions: int) -> int:
    for n in count(2):
        if len(get_prime_partitions(number=n, slots=n)) >= num_prime_partitions:
            return n
    return -1


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(77))
