#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Solution to Project Euler problem 43: Sub-string divisibility

Problem Statement:
The number, 1406357289, is a 0 to 9 pandigital number because it is made up of each of the digits
0 to 9 in some order, but it also has a rather interesting sub-string divisibility property.

Let d₁ be the 1st digit, d₂ be the 2nd digit, and so on. In this way, we note the following:
- d₂d₃d₄ = 406 is divisible by 2
- d₃d₄d₅ = 063 is divisible by 3
- d₄d₅d₆ = 635 is divisible by 5
- d₅d₆d₇ = 357 is divisible by 7
- d₆d₇d₈ = 572 is divisible by 11
- d₇d₈d₉ = 728 is divisible by 13
- d₈d₉d₁₀ = 289 is divisible by 17

Find the sum of all 0 to 9 pandigital numbers with this property.

Solution Approach:
This solution systematically generates and tests pandigital numbers:
1. Generate all permutations of digits 0-9
2. Filter out those starting with 0 (as they wouldn't be 10-digit numbers)
3. For each remaining permutation, check if consecutive 3-digit substrings satisfy the divisibility requirements
4. Sum all numbers that pass these tests

By checking each constraint in sequence, we can efficiently identify the special pandigital numbers
with the required divisibility properties.

Test Cases:
- The example in the problem, 1406357289, has the required property
- The total sum of all such numbers is 16695334890

URL: https://projecteuler.net/problem=43
Answer: 16695334890
"""
from itertools import permutations
from typing import Tuple

from euler.evaluator import evaluate_solutions, register_solution
from euler.types import ProblemArgs, ProblemArgsList

# The problem number from Project Euler (https://projecteuler.net/problem=43)
problem_number: int = 43

problem_args_list: ProblemArgsList = [
    ProblemArgs(
        kwargs={},  # No input parameters required
        answer=16695334890,  # The expected sum of all matching pandigital numbers
    ),
]


@register_solution(problem_number=problem_number, args_list=problem_args_list)
def sum_special_pandigital_numbers() -> int:
    """
    Find the sum of all 0-9 pandigital numbers with special divisibility properties.

    This solution finds pandigital numbers (using all digits 0-9 exactly once) where
    consecutive 3-digit substrings have specific divisibility properties. The approach
    generates permutations and filters them by the divisibility requirements specified
    in the problem.

    Returns:
        The sum of all 0-9 pandigital numbers with the required substring divisibility

    Example:
        >>> sum_special_pandigital_numbers()
        16695334890

    Note:
        The example number 1406357289 is included in the sum as it satisfies all constraints:
        - 406 is divisible by 2
        - 063 is divisible by 3
        - 635 is divisible by 5
        - 357 is divisible by 7
        - 572 is divisible by 11
        - 728 is divisible by 13
        - 289 is divisible by 17
    """
    divisors: Tuple[int, int, int, int, int, int, int] = (2, 3, 5, 7, 11, 13, 17)
    return sum(int(''.join(num_s)) for num_s in permutations('0123456789')
               if num_s[0] != '0'  # Skip numbers starting with 0
               and not any(int(''.join(num_s[i:i + 3])) % divisor != 0 for i, divisor in enumerate(divisors, start=1)))


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(problem_number))
