# !/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
Solution to Project Euler problem 9: Special Pythagorean Triplet

Problem Statement:
A Pythagorean triplet is a set of three natural numbers, a < b < c, for which,
a² + b² = c².

For example, 3² + 4² = 9 + 16 = 25 = 5².

There exists exactly one Pythagorean triplet for which a + b + c = 1000.
Find the product abc.

Solution Approach:
This solution employs an efficient search strategy to find Pythagorean triplets with specific sums:

1. Mathematical Constraints: Using the constraints of Pythagorean triplets and the sum requirement,
   we can significantly narrow the search space:
   - Since a < b < c and a + b + c = sum_sides, we know that a < sum_sides/3
   - For practical purposes, we can further constrain a < sum_sides/4 and b < sum_sides/2

2. Direct Calculation: Rather than searching for all three values independently, we calculate
   c directly as sum_sides - a - b, which guarantees that a + b + c = sum_sides.

3. Efficient Implementation: We use Python's generator expressions with next() to find the
   first matching triplet without creating full lists of all possible combinations.

4. Early Termination: The algorithm stops as soon as it finds a matching triplet, avoiding
   unnecessary computation since the problem states there is exactly one solution.

The time complexity is O(n²) where n is the sum_sides value, but the practical runtime
is much better due to the mathematical optimizations that limit the search space.

Test Cases:
- For sum_sides=12: Product = 60 (from the triplet 3,4,5 where 3+4+5=12 and 3²+4²=5²)
- For sum_sides=1000: Product = 31875000

URL: https://projecteuler.net/problem=9
Answer: 31875000
"""

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol

# Define test cases for validation
problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={'sum_sides': 12}, answer=60, ),  # First test case: sum = 12 (3,4,5) Expected answer: 3*4*5 = 60
    ProblemArgs(kwargs={'sum_sides': 1000}, answer=31875000, ),  # Second test case: sum = 1000 Expected answer 31875000
]


def solution(*, sum_sides: int) -> int | None:
    """
    Find the product of the Pythagorean triplet (a,b,c) with sum equal to sum_sides.

    A Pythagorean triplet is a set of three natural numbers (a < b < c) such that
    a² + b² = c². This function finds a triplet where a + b + c = sum_sides and
    returns their product (a*b*c).

    Args:
        sum_sides: The required sum of the three sides (a + b + c)

    Returns:
        int: The product a*b*c of the Pythagorean triplet
        None: If no Pythagorean triplet exists with the given sum

    Algorithm:
        1. Iterate through possible values of 'a' (optimized range)
        2. For each 'a', iterate through possible values of 'b' (optimized range)
        3. Calculate 'c' as sum_sides - a - b
        4. Check if a² + b² = c² (Pythagorean condition)
        5. Return the product a*b*c for the first triplet found

    Optimization notes:
        - 'a' must be less than sum_sides/4 due to constraints
        - 'b' must be at least 'a' and less than sum_sides/2
        - Using generator expression with next() for efficiency
    """
    try:
        return next(a * b * c
                    for a in range(1, sum_sides // 4 + 1)  # Optimized range for 'a'
                    for b in range(a, sum_sides // 2)  # Optimized range for 'b'
                    for c in (sum_sides - a - b,)  # Calculate 'c' directly
                    if a ** 2 + b ** 2 == c ** 2)  # Pythagorean condition
    except StopIteration:
        pass  # Return None if no triplet is found


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
