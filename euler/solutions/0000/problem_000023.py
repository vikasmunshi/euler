# !/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
Solution to Project Euler problem 23: Non-abundant Sums

Problem Statement:
A perfect number is a number for which the sum of its proper divisors is exactly equal to the number.
For example, the sum of the proper divisors of 28 would be 1 + 2 + 4 + 7 + 14 = 28, which means that
28 is a perfect number.

A number n is called deficient if the sum of its proper divisors is less than n and it is called
abundant if this sum exceeds n.

As 12 is the smallest abundant number (1 + 2 + 3 + 4 + 6 = 16), the smallest number that can be
written as the sum of two abundant numbers is 24. By mathematical analysis, it can be shown that all
integers greater than 28123 can be written as the sum of two abundant numbers. However, this upper
limit cannot be reduced any further by analysis even though it is known that the greatest number
that cannot be expressed as the sum of two abundant numbers is less than this limit.

Find the sum of all the positive integers which cannot be written as the sum of two abundant numbers.

Solution Approach:
This problem can be broken down into several discrete steps:

1. Classification of Numbers: We need to identify which numbers are abundant (sum of proper divisors
   exceeds the number itself). This requires an efficient algorithm to calculate the sum of proper
   divisors.

2. Identifying Abundant Numbers: We generate a list of all abundant numbers below the given upper
   limit (28123). Since 12 is the smallest abundant number, we can start our search from there.

3. Generating Sums: We compute all possible sums of two abundant numbers (which may include sums
   of an abundant number with itself). These are the numbers that CAN be expressed as the sum of
   two abundant numbers.

4. Finding Non-Abundant Sums: Using set operations, we determine which positive integers below
   the limit CANNOT be expressed as the sum of two abundant numbers.

5. Computing the Final Sum: We add up all these non-expressible numbers to get our answer.

Mathematical Note:
The upper bound of 28123 is significant in this problem. Mathematical analysis has proven that
all integers above this limit can be expressed as the sum of two abundant numbers. While the
actual highest non-expressible number is likely lower, this bound simplifies our search space.

URL: https://projecteuler.net/problem=23
Answer: 4179871
"""
from euler.types import ProblemArgsList, ProblemArgs, SolutionProtocol

problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={}, answer=4179871, ),
]


def sum_proper_divisors(n: int) -> int:
    """Calculate the sum of all proper divisors of a number.

    A proper divisor is any positive integer that divides n evenly, excluding n itself.
    This function uses an efficient algorithm that only checks divisors up to the square root.

    Algorithm Details:
    1. We know that 1 is always a proper divisor of any number > 1, so we start with sum = 1
    2. Instead of checking all numbers from 2 to n-1, we only iterate up to sqrt(n)
    3. For each divisor i we find, we also add n/i as a divisor (except when i = sqrt(n))
    4. This optimization reduces the time complexity from O(n) to O(sqrt(n))

    Mathematical Background:
    For any divisor i of n (where i ≤ sqrt(n)), n/i is also a divisor of n.
    This property allows us to find all divisors by only checking up to the square root.

    Complexity Analysis:
    - Time Complexity: O(sqrt(n))
    - Space Complexity: O(1)

    Edge Cases:
    - For n = 1, the sum of proper divisors is 0 (as 1 has no proper divisors)
    - For prime numbers, the sum of proper divisors is always 1

    Args:
        n: A positive integer whose proper divisors will be summed

    Returns:
        The sum of all proper divisors of n

    Examples:
        >>> sum_proper_divisors(12)
        16  # 1 + 2 + 3 + 4 + 6 = 16
        >>> sum_proper_divisors(28)
        28  # 1 + 2 + 4 + 7 + 14 = 28 (perfect number)
        >>> sum_proper_divisors(15)
        9   # 1 + 3 + 5 = 9 (deficient number)
        >>> sum_proper_divisors(12)
        16  # 1 + 2 + 3 + 4 + 6 = 16 (abundant number as 16 > 12)
    """
    n_sqrt = int(n ** 0.5)
    return 1 + sum(i + n // i for i in range(2, n_sqrt + 1) if n % i == 0) - (n_sqrt if n_sqrt ** 2 == n else 0)


def solution() -> int:
    """Solve Project Euler problem 23: Non-abundant sums.

    Finds the sum of all positive integers that cannot be expressed as the sum of two abundant numbers.

    Implementation Details:
    1. Identify Abundant Numbers:
       - We know 12 is the smallest abundant number
       - We only need to check numbers up to 28123-12 (as we need pairs of abundant numbers)
       - For each number i, we calculate sum_proper_divisors(i) and compare with i
       - If the sum exceeds i, then i is abundant and added to our list

    2. Generate Sums of Abundant Numbers:
       - We use a generator expression to create all possible pairs (a+b) of abundant numbers
       - This includes pairs where a=b (same number used twice)
       - The generator approach is memory-efficient as it doesn't store all combinations at once

    3. Find Non-Abundant Sums:
       - Create a set of all integers from 1 to 28123
       - Create a set of all abundant sums
       - Use set difference operation to find numbers that aren't expressible as abundant sums
       - Sum these numbers for the final result

    Optimizations:
    - Range Limitation: Only checking numbers up to 28123 (mathematical bound)
    - Efficient Abundant Number Identification: Starting from 12 and using the optimized
      sum_proper_divisors function
    - Memory Efficiency: Using generator expressions to avoid storing all pairs in memory
    - Set Operations: Using set difference for efficient filtering of non-expressible numbers

    Time and Space Analysis:
    - Time Complexity: O(N*sqrt(N) + A²), where N is the upper limit (28123) and A is the
      number of abundant numbers below N
    - Space Complexity: O(N + A + A²) for storing the sets of integers, abundant numbers,
      and sums of abundant numbers

    Returns:
        The sum of all positive integers which cannot be written as the sum of two abundant numbers
    """
    # Find all abundant numbers between 12 (smallest known) and the upper limit minus 12
    # An abundant number has a sum of proper divisors greater than itself
    abundant_numbers = [i for i in range(12, 28123 - 12) if sum_proper_divisors(i) > i]

    # Generate all possible sums of two abundant numbers using a generator expression
    # This is memory-efficient as it doesn't store all combinations at once
    # The nested loops create all combinations (a,b) where both a and b are abundant
    abundant_sums = (a + b for a in abundant_numbers for b in abundant_numbers)

    # Find numbers that cannot be expressed as the sum of two abundant numbers:
    # 1. Create a set of all integers from 1 to the upper limit
    # 2. Create a set of all possible sums of abundant numbers
    # 3. Use set difference to find numbers that are not in the abundant sums set
    # 4. Sum these numbers to get the final answer
    return sum(set(range(1, 28123 + 1)) - set(abundant_sums))


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
