# !/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
Solution to Project Euler problem 5: Smallest Multiple

Problem Statement:
2520 is the smallest number that can be divided by each of the numbers from 1 to 10 without any remainder.
What is the smallest positive number that is evenly divisible by all of the numbers from 1 to 20?

Solution Approach:
This problem asks for the least common multiple (LCM) of all integers from 1 to n.

The implementation uses the following mathematical concepts and optimizations:

1. The LCM of two numbers a and b can be calculated using the formula: LCM(a,b) = (a*b)/GCD(a,b)
   where GCD is the greatest common divisor

2. Python's math.gcd function efficiently computes the greatest common divisor using
   the Euclidean algorithm

3. The functools.reduce function elegantly extends the LCM calculation to multiple numbers by
   applying the LCM operation cumulatively across the range

4. Since the LCM of 1 and any number is that number itself, we start the range from 2
   and use 1 as the initial value for reduce

The solution has O(n log n) time complexity, which is efficient even for large values of n.

Test Cases:
- For n=10: 2520
- For n=20: 232792560

URL: https://projecteuler.net/problem=5
Answer: 232792560
"""
from functools import reduce
from math import gcd

from euler.evaluator import evaluate_solutions, register_solution
from euler.types import ProblemArgs, ProblemArgsList

# The problem number from Project Euler (https://projecteuler.net/problem=5)
problem_number: int = 5

# Define the test cases for validating the solution
problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={'n': 10}, answer=2520, ),
    ProblemArgs(kwargs={'n': 20}, answer=232792560, ),
    ProblemArgs(kwargs={'n': 50}, answer=3099044504245996706400, ),
    ProblemArgs(kwargs={'n': 100}, answer=69720375229712477164533808935312303556800, ),
]


@register_solution(problem_number=problem_number, args_list=problem_args_list)
def least_common_multiple_of_1_to_n(*, n: int) -> int:
    """Calculate the smallest positive number divisible by all integers from 1 to n.

    This function computes the least common multiple (LCM) of all integers from 1 to n.
    It uses the mathematical property that LCM(a,b) = (a*b)/gcd(a,b) and extends it
    to multiple numbers using the reduce function.

    Args:
        n (int): The upper limit of the range of integers to consider.
            Must be a positive integer.

    Returns:
        int: The smallest positive number that is evenly divisible by all
            integers from 1 to n.

    Time Complexity: O(n log n) - iterating through n numbers with gcd calculation
    Space Complexity: O(1) - uses constant extra space regardless of input size
    """
    return reduce(lambda x, y: x * y // gcd(x, y), range(2, n + 1), 1)


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(problem_number))
