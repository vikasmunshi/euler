#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
Solution to Project Euler problem 78:

Problem Statement:
Let p(n) represent the number of different ways in which n coins can be separated into piles.
For example, five coins can be separated into piles in exactly seven different ways, so p(5)=7.

OOOOO
OOOO   O
OOO   OO
OOO   O   O
OO   OO   O
OO   O   O   O
O   O   O   O   O

Find the least value of n for which p(n) is divisible by one million.

Solution Approach:

Test Cases:

URL: https://projecteuler.net/problem=78
Answer: 55374
"""
from itertools import count

from euler.evaluator import evaluate_solutions, register_solution
from euler.types import ProblemArgs, ProblemArgsList
from euler.utils.integer_partitions import num_partitions

# The problem number from Project Euler (https://projecteuler.net/problem=78)
problem_number: int = 78

# Define the test cases for validating the solution
problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={'divisor': 10 ** 3}, answer=449, ),
    ProblemArgs(kwargs={'divisor': 10 ** 6}, answer=55374, ),
]


# Register this function as a solution for problem #78 with test cases
@register_solution(problem_number=problem_number, args_list=problem_args_list)
def count_divisible_by_partitions(*, divisor: int) -> int:
    for n in count(2):
        if num_partitions(number=n) % divisor == 0:
            return n
    return -1


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(problem_number))
