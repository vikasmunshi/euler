#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Solution to Project Euler problem 52: Permuted multiples

Problem Statement:
It can be seen that the number, 125874, and its double, 251748, contain exactly the same digits, 
but in a different order.

Find the smallest positive integer, x, such that 2x, 3x, 4x, 5x, and 6x, contain the same digits.

Solution Approach:
This solution systematically searches for the target number by:

1. Iterating through positive integers in ascending order
2. For each integer, calculating its first N multiples (2x, 3x, etc.)
3. Converting each multiple to a string and sorting its digits to create a canonical
   representation regardless of digit order
4. Using a set to efficiently determine if all multiples contain the same digits
   - If the set contains only one element, all multiples have identical digits

For efficiency, the solution:
- Limits the search space to reasonable values (using sys.maxsize//multiples)
- Uses a compact set comprehension to check all multiples simultaneously
- Implements validation to ensure the input parameter is within reasonable bounds

Test Cases:
- For multiples=2: 125874 (125874 and 251748 have the same digits)
- For multiples=3,4,5,6: 142857 (all multiples up to 6x contain the same digits)
  * 142857 × 2 = 285714
  * 142857 × 3 = 428571
  * 142857 × 4 = 571428
  * 142857 × 5 = 714285
  * 142857 × 6 = 857142

URL: https://projecteuler.net/problem=52
Answer: 142857
"""
import sys

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol

problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={'multiples': 2}, answer=125874, ),
    ProblemArgs(kwargs={'multiples': 3}, answer=142857, ),
    ProblemArgs(kwargs={'multiples': 4}, answer=142857, ),
    ProblemArgs(kwargs={'multiples': 5}, answer=142857, ),
    ProblemArgs(kwargs={'multiples': 6}, answer=142857, ),
]


def solution(*, multiples: int) -> int:
    """
    Find the smallest positive integer whose multiples contain the same digits.

    This function searches for the smallest number x where x, 2x, 3x, ..., up to
    multiples×x all contain exactly the same digits (in any order). It works by
    converting each multiple to a string, sorting its digits, and comparing them.

    Args:
        multiples: The number of consecutive multiples to check (between 2 and 6)

    Returns:
        The smallest positive integer with the permuted multiples property

    Examples:
        >>> solution(multiples=2)
        125874  # 125874 and 251748 contain the same digits
        >>> solution(multiples=6)
        142857  # 142857, 285714, 428571, 571428, 714285, 857142 all contain the same digits

    Raises:
        ValueError: If multiples is not between 2 and 6, or if no solution is found
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
    # This block is executed when the Python module is run directly.
    # It evaluates the solution function to ensure its correctness against test cases.

    # Importing required modules: `module_main` manages how the solution is invoked and tested,
    # while `cast` helps with type safety in passing the solution as a `SolutionProtocol`.
    from typing import cast
    from euler.evaluator import module_main

    # The `module_main` function handles the evaluation process by:
    # 1. Extracting the problem number from the file name for contextual usage.
    # 2. Accepting command-line arguments to configure execution, e.g., timeout or threading options.
    # 3. Running the `solution` function for all test cases defined in `problem_args_list`.
    # 4. Outputting the test results, including details such as whether the test passed/failed and time taken.
    # 5. Returning an appropriate exit code (exit code 0 indicates success, non-zero for failures).

    # The `SystemExit` ensures the program exits with the exit code returned by `module_main`.
    raise SystemExit(module_main(module_name=__file__,
                                 solution=cast(SolutionProtocol, solution),
                                 args_list=problem_args_list))
