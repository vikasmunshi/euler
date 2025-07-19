#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Solution to Project Euler problem 34: Digit factorials

Problem Statement:
145 is a curious number, as 1! + 4! + 5! = 1 + 24 + 120 = 145.

Find the sum of all numbers which are equal to the sum of the factorial of their digits.

Note: As 1! = 1 and 2! = 2 are not sums they are not included.

Solution Approach:
This solution systematically searches for numbers that equal the sum of their digit factorials.
The approach is optimized based on mathematical reasoning to limit the search space:

1. An upper bound is established by recognizing that for any d-digit number where d ≥ 8:
   - The largest possible sum of digit factorials would be d×9! = d×362,880
   - This sum cannot exceed 8×9! = 2,903,040 for an 8-digit number
   - But the smallest 8-digit number is 10,000,000, which exceeds this maximum sum
   - Therefore, we only need to check numbers up to 7 digits

2. The implementation uses combinations_with_replacement to efficiently generate all
   possible digit combinations, avoiding redundant calculations when the same digit appears
   multiple times.

3. For each combination of digits, the algorithm:
   - Calculates the sum of their factorials
   - Verifies that this sum has the expected number of digits
   - Confirms that all the original digits appear in the sum (possibly in a different order)
   - Double-checks that the sum indeed equals the sum of factorials of its own digits

This approach significantly reduces the search space from millions of numbers to a much
smaller set of possible combinations.

URL: https://projecteuler.net/problem=34
Answer: 40730
"""
from itertools import combinations_with_replacement

from euler.evaluator import evaluate_solutions, register_solution
from euler.types import ProblemArgs, ProblemArgsList

# The problem number from Project Euler (https://projecteuler.net/problem=34)
problem_number: int = 34

problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={}, answer=40730, ),
]


@register_solution(problem_number=problem_number, args_list=problem_args_list)
def sum_natural_numbers_equal_to_sum_digit_factorials() -> int:
    """Find the sum of all numbers equal to the sum of the factorials of their digits.

    This function identifies all numbers where the sum of the factorials of each digit
    equals the number itself. It excludes 1 and 2 as specified in the problem statement.

    Returns:
        The sum of all numbers that equal the sum of the factorials of their digits

    Example:
        >>> sum_natural_numbers_equal_to_sum_digit_factorials()
        40730  # Includes numbers like 145 (1! + 4! + 5! = 145)
    """
    upper_bound_num_digits = 7 + 1
    factorial = {'0': 1, '1': 1, '2': 2, '3': 6, '4': 24, '5': 120, '6': 720, '7': 5040, '8': 40320, '9': 362880}
    return sum(
        int(num)
        for num_digits in range(2, upper_bound_num_digits)
        for digits in combinations_with_replacement('0123456789', num_digits)
        for num in (str(sum(factorial[d] for d in digits)),)
        if len(num) == num_digits
        and all(digit in num for digit in digits)
        and num == str(sum(factorial[n] for n in num))
    )


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(problem_number))
