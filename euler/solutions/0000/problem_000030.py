#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 30
# https://projecteuler.net/problem=30
# Answer: 443839
# Notes: 
import textwrap
from itertools import combinations_with_replacement
from math import ceil, log

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol

problem_args_list: ProblemArgsList = [
    ProblemArgs(
        kwargs={'n': 4},
        answer=19316,
    ),
    ProblemArgs(
        kwargs={'n': 5},
        answer=443839,
    ),
]


def solution(*, n: int) -> int:
    """Calculate the sum of all numbers that equal the sum of nth powers of their digits.

    This function finds all numbers where the sum of the nth powers of their digits
    equals the number itself. For example, with n=4, we find numbers like 1634 where
    1^4 + 6^4 + 3^4 + 4^4 = 1634. The solution then returns the sum of all such numbers.

    Mathematical Approach:
    1. Determine an upper bound for the number of digits by solving the inequality:
       - A d-digit number is at most 10^d - 1
       - The sum of nth powers of d digits is at most d*(9^n)
       - For large enough d, d*(9^n) < 10^d - 1, making it impossible to find matches
       - We solve for d where d*(9^n) and 10^d have similar magnitudes
       - The formula `ceil(log(n * 9 ** n, 10))` implements this bound by:
         a. Finding the value of n×9^n, which represents a safe upper estimate
         b. Taking log base 10 gives us approximately how many digits this number has
         c. Ceiling function ensures we don't underestimate the bound
         d. Example: For n=5, this gives 6 digits as our search limit instead of checking 
            all numbers up to some arbitrary limit like 1,000,000

    2. Generate all possible multisets of digits up to the calculated bound using
       combinations_with_replacement, which efficiently handles all digit combinations
       including repeats.

    3. For each combination of digits:
       - Calculate the sum of the nth powers of these digits
       - Check if this sum creates a number that equals the sum of the nth powers of its own digits
       - Exclude single-digit numbers (like 1) as they're not considered sums

    Args:
        n: The power to which each digit is raised

    Returns:
        The sum of all numbers that can be written as the sum of the nth powers of their digits
    """
    upper_bound_num_digits = ceil(log(n * 9 ** n, 10))
    return sum(num for digits in combinations_with_replacement(range(10), upper_bound_num_digits)
               if (num := sum(x ** n for x in digits)) > 9 and num == sum(int(x) ** n for x in str(num)))


# Explicitly annotate that this function implements SolutionProtocol
solution: SolutionProtocol

solution.__doc__ = textwrap.dedent(r'''
solution to Project Euler problem 30
https://projecteuler.net/problem=30
Surprisingly there are only three numbers that can be written as the sum of fourth powers of their digits:
1634 = 1^4 + 6^4 + 3^4 + 4^4
8208 = 8^4 + 2^4 + 0^4 + 8^4
9474 = 9^4 + 4^4 + 7^4 + 4^4
As 1 = 1^4 is not a sum it is not included.
The sum of these numbers is 1634 + 8208 + 9474 = 19316.
Find the sum of all the numbers that can be written as the sum of fifth powers of their digits.

    Mathematical Approach:
    1. Determine an upper bound for the number of digits by solving the inequality:
       - A d-digit number is at most 10^d - 1
       - The sum of nth powers of d digits is at most d*(9^n)
       - For large enough d, d*(9^n) < 10^d - 1, making it impossible to find matches
       - We solve for d where d*(9^n) and 10^d have similar magnitudes
       - The formula `upper_bound_num_digits = ceil(log(n * 9 ** n, 10))` calculates this bound:
         a. We need to find the smallest d where d × 9^n < 10^d
         b. Taking log base 10 of both sides: log10(d × 9^n) < d
         c. Using log properties: log10(d) + n × log10(9) < d
         d. For most values of n, log10(d) is small compared to n × log10(9)
         e. We use n * 9^n as a conservative estimate and take its log
         f. Ceiling function ensures we get an integer upper bound
         g. Example for n=5: 9^5 = 59,049; 5×9^5 = 295,245; log10(295,245) ≈ 5.47; ceil(5.47) = 6

    2. Generate all possible multisets of digits up to the calculated bound using
       combinations_with_replacement, which efficiently handles all digit combinations
       including repeats.

    3. For each combination of digits:
       - Calculate the sum of the nth powers of these digits
       - Check if this sum creates a number that equals the sum of the nth powers of its own digits
       - Exclude single-digit numbers (like 1) as they're not considered sums

''').strip()

if __name__ == '__main__':
    # When run directly, evaluate the solution with test cases
    # Import required modules for evaluating the solution
    from euler.evaluator import evaluate_solution
    from euler.cli import parser
    from euler.logger import logger

    # Parse command-line arguments
    args = parser.parse_args()

    # Set the logging level based on command-line arguments
    logger.setLevel(args.log_level)

    # Extract timeout and maximum worker threads from arguments
    timeout, max_workers = args.timeout, args.max_workers

    # Run the solution with the specified test cases and parameters
    # This validates that our implementation gives the correct answers
    evaluate_solution(solution=solution, args_list=problem_args_list, timeout=timeout, max_workers=max_workers)
