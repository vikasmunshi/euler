# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 52
# https://projecteuler.net/problem=52
# Answer: 142857
# Notes:
import sys
from typing import cast

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol

# A list of test cases for the solution function.
# Each test case defines:
#  - multiples: The number of consecutive multiples that should contain the same digits
#  - answer: The expected smallest integer meeting the criteria for the given 'multiples' parameter
# 
# For example:
#  - When 'multiples' is 2, the smallest integer is 125874 (125874 and 2×125874=251748 contain the same digits)
#  - When 'multiples' is 6, the smallest integer is 142857 (142857, 2×142857, 3×142857, 4×142857, 5×142857, 
#    and 6×142857 all contain the same digits)
# 
# Note: These test cases validate various scenarios for the solution and ensure correct implementation
# across different input parameters.
problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={'multiples': 2}, answer=125874, ),
    ProblemArgs(kwargs={'multiples': 3}, answer=142857, ),
    ProblemArgs(kwargs={'multiples': 4}, answer=142857, ),
    ProblemArgs(kwargs={'multiples': 5}, answer=142857, ),
    ProblemArgs(kwargs={'multiples': 6}, answer=142857, ),
]


def solution(*, multiples: int) -> int:
    """
    solution to Project Euler problem 52
    https://projecteuler.net/problem=52
    It can be seen that the number, 125874, and its double, 251748, contain exactly the same digits,
    but in a different order.
    Find the smallest positive integer, x, such that 2x, 3x, 4x, 5x, and 6x, contain the same digits.

    Finds the smallest positive integer such that the digits of its multiples up to a given
    count are permutations of each other.

    This function iterates from 1 upward to find the smallest number whose first `multiples`
    multiples all have the exact same digits in any order. If no solution is found within
    the range of the integer space, a ValueError is raised. The algorithm relies on
    converting the numbers to strings, sorting their digits, and checking for equivalence.

    Parameters:
        multiples (int): The number of multiples to evaluate for permutation checks.

    Returns:
        int: The smallest integer that meets the described criteria.

    Raises:
        ValueError: If no valid integer is found within the search limit.
    """
    if not (isinstance(multiples, int) and 1 < multiples < 7):
        # For multiples=7 or higher, there likely does not exist a solution where a positive integer and all its first n
        # multiples contain the exact same digits.
        raise ValueError('multiples must be an integer between 2 and 6, both inclusive.')
    multiples_range = tuple(range(1, multiples + 1))
    for i in range(1, sys.maxsize // multiples):  # not considering the know solution for multiples = 2
        # 1. `for multiple in multiples_range` - Iterates through each multiple (1, 2, 3, etc. up to the specified 'multiples' parameter)
        # 2. `i * multiple` - Calculates each multiple of the current number i being tested
        # 3. `str(i * multiple)` - Converts each multiple to a string, so we can work with its individual digits
        # 4. `sorted(str(i * multiple))` - Sorts the digits of each multiple in ascending order
        #     - For example, if i=142857 and multiple=2, then i*multiple=285714, and sorted would yield ['1','2','4','5','7','8']
        #
        # 5. `''.join(sorted(str(i * multiple)))` - Joins the sorted list (unhashable) of digits back into a string (hashable)
        #     - This produces a canonical representation of the digit set regardless of their original order
        #     - Example: 285714 becomes '124578'
        #
        # 6. `{...}` - Creates a set of these sorted digit strings for all multiples
        #     - A set only contains unique elements, so if all multiples have the same digits (in any order), this set will contain only one element
        #
        # 7. `len({...}) == 1` - Checks if the set has exactly one element
        #     - If true, all multiples contain exactly the same digits (just arranged differently)
        #     - If false, at least one multiple has a different set of digits
        if len({''.join(sorted(str(i * multiple))) for multiple in multiples_range}) == 1:
            return i
    else:
        raise ValueError('No solution found')


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
    evaluate_solution(solution=cast(SolutionProtocol, solution), args_list=problem_args_list, timeout=timeout,
                      max_workers=max_workers)
