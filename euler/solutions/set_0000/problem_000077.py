# !/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
Solution to Project Euler problem 77:

Problem Statement:
It is possible to write ten as the sum of primes in exactly five different ways:


7 + 3
5 + 5
5 + 3 + 2
3 + 3 + 2 + 2
2 + 2 + 2 + 2 + 2


What is the first value which can be written as the sum of primes in over five thousand different ways?

Solution Approach:

Test Cases:

URL: https://projecteuler.net/problem=77
Answer: 71
"""
from itertools import count

from euler.evaluator import evaluate_solutions, register_solution
from euler.types import ProblemArgs, ProblemArgsList
from euler.utils.integer_partitions import get_prime_partitions, num_prime_integer_partitions

# The problem number from Project Euler (https://projecteuler.net/problem=77)
problem_number: int = 77

# Define the test cases for validating the solution
problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={'num_prime_partitions': 5}, answer=10, ),
    ProblemArgs(kwargs={'num_prime_partitions': 5 * 10 ** 1}, answer=25, ),
    ProblemArgs(kwargs={'num_prime_partitions': 5 * 10 ** 2}, answer=45, ),
    ProblemArgs(kwargs={'num_prime_partitions': 5 * 10 ** 3}, answer=71, ),
    ProblemArgs(kwargs={'num_prime_partitions': 5 * 10 ** 4}, answer=104, ),
]


# Register this function as a solution for problem #77 with test cases
@register_solution(problem_number=problem_number, args_list=problem_args_list)
def count_prime_partitions(*, num_prime_partitions: int) -> int:
    for n in count(1):
        if num_prime_integer_partitions(number=n, slots=n) >= num_prime_partitions:
            return n
    return -1


# Register this function as a solution for problem #77 with test cases
@register_solution(problem_number=problem_number, args_list=problem_args_list[:-3])
def list_prime_partitions(*, num_prime_partitions: int) -> int:
    for n in count(2):
        if len(get_prime_partitions(number=n, slots=n)) >= num_prime_partitions:
            return n
    return -1


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(problem_number))
