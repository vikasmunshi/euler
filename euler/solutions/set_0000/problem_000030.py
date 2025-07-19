#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Solution to Project Euler problem 30: Digit fifth powers

Problem Statement:
Surprisingly there are only three numbers that can be written as the sum of fourth powers of their digits:

1634 = 1^4 + 6^4 + 3^4 + 4^4
8208 = 8^4 + 2^4 + 0^4 + 8^4
9474 = 9^4 + 4^4 + 7^4 + 4^4

As 1 = 1^4 is not a sum it is not included.
The sum of these numbers is 1634 + 8208 + 9474 = 19316.

Find the sum of all the numbers that can be written as the sum of fifth powers of their digits.

Solution Approach:
This implementation finds numbers where the sum of the nth powers of their digits equals
the number itself. The approach uses mathematical reasoning to efficiently bound the search space:

1. Determine an upper bound for the number of digits by finding where the maximum possible
   sum of digit powers (d×9^n) becomes less than the smallest d-digit number (10^(d-1)).

2. Use combinations_with_replacement to generate all possible multisets of digits up to
   the calculated bound, which efficiently handles all possible digit combinations.

3. For each combination, calculate the sum of nth powers and check if this matches a number
   that would be formed by those digits, excluding single-digit numbers as they're not considered sums.

The solution uses the walrus operator (:=) to efficiently assign and test values in a single expression.

Test Cases:
- For n=4, the answer is 19316 (sum of 1634, 8208, and 9474)
- For n=5, the answer is 443839

URL: https://projecteuler.net/problem=30
Answer: 443839
"""
from itertools import combinations_with_replacement
from math import ceil, log

from euler.evaluator import evaluate_solutions, register_solution
from euler.types import ProblemArgs, ProblemArgsList

# The problem number from Project Euler (https://projecteuler.net/problem=30)
problem_number: int = 30

# Define the test cases for validating the solution
problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={'n': 4}, answer=19316, ),
    ProblemArgs(kwargs={'n': 5}, answer=443839, ),
]


@register_solution(problem_number=problem_number, args_list=problem_args_list)
def sum_n_digit_numbers_that_equal_nth_power_digits(*, n: int) -> int:
    """Calculate the sum of all numbers that equal the sum of nth powers of their digits.

    This function finds all numbers where the sum of the nth powers of their digits
    equals the number itself, then returns the sum of all such numbers.

    Args:
        n: The power to which each digit is raised

    Returns:
        The sum of all numbers that can be written as the sum of the nth powers of their digits

    Example:
        >>> sum_n_digit_numbers_that_equal_nth_power_digits(n=4)
        19316  # Sum of 1634, 8208, and 9474
        >>> sum_n_digit_numbers_that_equal_nth_power_digits(n=5)
        443839
    """
    upper_bound_num_digits = ceil(log(n * 9 ** n, 10))
    return sum(num for digits in combinations_with_replacement(range(10), upper_bound_num_digits)
               if (num := sum(x ** n for x in digits)) > 9 and num == sum(int(x) ** n for x in str(num)))


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(problem_number))
