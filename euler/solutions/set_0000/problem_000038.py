#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Solution to Project Euler problem 38: Pandigital multiples

Problem Statement:
Take the number 192 and multiply it by each of 1, 2, and 3:
192 × 1 = 192
192 × 2 = 384
192 × 3 = 576

By concatenating each product we get the 1 to 9 pandigital, 192384576. We will call 192384576 the concatenated product
of 192 and (1,2,3).

The same can be achieved by starting with 9 and multiplying by 1, 2, 3, 4, and 5, giving the pandigital, 918273645,
which is the concatenated product of 9 and (1,2,3,4,5).

What is the largest 1 to 9 pandigital 9-digit number that can be formed as the concatenated product of an integer with
(1,2, ..., n) where n > 1?

Solution Approach:
This solution efficiently searches for the largest 9-digit pandigital number by examining
different combinations of starting numbers and sequence lengths. For each sequence length n,
we determine the largest possible starting number x that could produce a 9-digit result,
then work downward until finding a valid pandigital or exhausting possibilities.

Key optimizations:
1. Starting with larger values of n and x to maximize chances of finding larger pandigitals first
2. Using appropriate upper limits for each sequence length n to avoid unnecessary checks
3. Early termination once a valid pandigital is found for a given n

Examples:
- 192 × (1,2,3) produces 192384576 (pandigital)
- 9 × (1,2,3,4,5) produces 918273645 (pandigital)
- 9327 × (1,2) produces 932718654 (the largest possible pandigital)

URL: https://projecteuler.net/problem=38
Answer: 932718654
"""
from euler.evaluator import evaluate_solutions, register_solution
from euler.types import ProblemArgs, ProblemArgsList

# The problem number from Project Euler (https://projecteuler.net/problem=38)
problem_number: int = 38

problem_args_list: ProblemArgsList = [
    ProblemArgs(
        kwargs={},  # No parameters needed for this problem
        answer=932718654,  # The largest pandigital concatenated product
    ),
]


@register_solution(problem_number=problem_number, args_list=problem_args_list)
def longest_pandigital_number() -> int:
    """
    Find the largest 1-9 pandigital number formed as a concatenated product.

    This solution searches for the largest 9-digit number that contains each digit
    from 1 to 9 exactly once and can be formed by concatenating the products of an
    integer with the sequence (1,2,...,n) where n > 1. The algorithm examines
    different combinations of starting numbers and sequence lengths, prioritizing
    those more likely to produce larger pandigitals.

    Returns:
        The largest 9-digit pandigital number formed as a concatenated product

    Example:
        >>> longest_pandigital_number()
        932718654
    """
    result = 0

    # Consider different sequence lengths (n) and corresponding maximum starting numbers (x)
    # We pair each sequence length with the largest possible starting number that could
    # produce a 9-digit result when concatenated. Start with n=2 as specified in the problem.
    # For larger n values, the maximum possible x becomes smaller to keep the result at 9 digits.
    for n, x in ((2, 9876),  # For n=2, x can be up to 4 digits (concatenating x and 2x)
                 (3, 987),  # For n=3, x can be up to 3 digits (concatenating x, 2x, and 3x)
                 (4, 98),  # For n=4, x can be up to 2 digits
                 (5, 9),  # For n=5 and above, x must be a single digit
                 (6, 9),
                 (7, 9),
                 (8, 9),
                 (9, 9)):

        # Start from the maximum x and work downward
        while x > 0:
            # Concatenate the products of x with the sequence (1,2,...,n)
            number = ''.join([str(i * x) for i in range(1, n + 1)])

            # Check if the result is a 9-digit 1-9 pandigital (contains all digits 1-9 exactly once)
            is_pandigital = (len(number) == 9 and set(number) == set('123456789'))
            if is_pandigital:
                result = max(result, int(number))
                break  # Found the largest for this n, move to the next n (since we start from largest x)

            x -= 1  # Try a smaller x

    return result


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(problem_number))
