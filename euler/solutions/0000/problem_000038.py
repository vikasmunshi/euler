#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Solution to Project Euler problem 38: Pandigital Multiples
# https://projecteuler.net/problem=38
# Answer: 932718654
#
# PROBLEM DESCRIPTION:
# Take the number 192 and multiply it by each of 1, 2, and 3:
# 192 × 1 = 192
# 192 × 2 = 384
# 192 × 3 = 576
# By concatenating each product, we get the 1-9 pandigital number 192384576.
# We call 192,384,576 the concatenated product of 192 and (1,2,3).
#
# The same can be achieved by starting with 9 and multiplying by 1, 2, 3, 4, and 5,
# giving the pandigital 918273645, which is the concatenated product of 9 and (1,2,3,4,5).
#
# What is the largest 1-9 pandigital 9-digit number that can be formed as the concatenated
# product of an integer with (1,2,...,n) where n > 1?
#
# SOLUTION APPROACH:
# 1. Recognize that the problem requires finding a number x and a sequence length n
#    such that concatenating the products x×1, x×2, ..., x×n gives a 9-digit pandigital
#    number (containing digits 1-9 exactly once)
# 2. Since we want a 9-digit result and n must be at least 2, we can limit our search space:
#    - For n=2: x must produce 4 or 5 digits when multiplied by 1 (so x < 10000)
#    - For n=3: x must produce 3 digits when multiplied by 1 (so x < 1000)
#    - For n=4: x must produce 2 digits when multiplied by 1 (so x < 100)
#    - For n=5 to n=9: x must be a single digit (so x < 10)
# 3. Since we want the largest pandigital, we start from the largest possible x for each n
#    and work downward
# 4. For each combination of n and x, check if the concatenated product is pandigital
#
# OPTIMIZATIONS:
# - Start with larger values of x for each n since we want the largest pandigital
# - Break the search for each n once a valid pandigital is found
# - Use string operations for efficient concatenation and digit checking
# - Calculate upper limits for x based on the constraints of the problem
#
# MATHEMATICAL INSIGHTS:
# - For a 9-digit pandigital result, the number of digits in x and n must satisfy:
#   length(x) * n + additional_digits = 9
# - The digit 9 must appear in the result, and since we want the largest number,
#   it's likely that 9 will be one of the first digits
# - The answer must start with 9 to be the largest possible pandigital
#
# TIME COMPLEXITY: O(n * x) where n is the maximum multiplier and x is the maximum starting number
# SPACE COMPLEXITY: O(1) - constant space used regardless of input size
import textwrap
from typing import cast

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol

# Test case for the pandigital multiples problem
#
# There is only one test case for this problem since:
# 1. The problem has a unique answer (the largest pandigital concatenated product)
# 2. No parameters are needed to customize the solution
#
# The expected answer is 932,718,654, which is the concatenated product of 9327 and (1,2):
# 9327 × 1 = 9327
# 9327 × 2 = 18654
# Concatenated: 932718654 (pandigital with digits 1-9)
problem_args_list: ProblemArgsList = [
    ProblemArgs(
        kwargs={},  # No parameters needed for this problem
        answer=932718654,  # The largest pandigital concatenated product
    ),
]


def largest_pan_digital_multiple() -> int:
    """Find the largest 1-9 pandigital number formed as a concatenated product.

    This function finds the largest 9-digit number that contains each digit from 1 to 9
    exactly once (pandigital) and can be formed by concatenating the products of a number x
    with the sequence (1,2,...,n) where n > 1.

    For example,
    - 192 produces the pandigital 192384576 when multiplied by (1,2,3)
    - 9 produces the pandigital 918273645 when multiplied by (1,2,3,4,5)

    The implementation follows these steps:
    1. For each reasonable combination of sequence length n and starting number x:
       a. Calculate the concatenated product of x with the sequence (1,2,...,n)
       b. Check if the result is a 9-digit 1-9 pandigital number
       c. Keep track of the largest such number found
    2. Return the largest pandigital number discovered

    The search space is optimized by starting with larger values of x for each n
    and using appropriate upper limits for x based on digit constraints.

    Returns:
        The largest 9-digit pandigital number formed as a concatenated product

    Notes:
        - The function checks various sequence lengths from n=2 to n=9
        - For each n, it starts with the largest possible x that could produce a 9-digit result
        - The search for each n terminates once a valid pandigital is found (since we start
          from the largest possible x, this will be the largest for that n)
        - The final result is 932,718,654, formed by 9327 × (1,2)
    """
    result = 0

    # Consider different sequence lengths (n) and corresponding maximum starting numbers (x)
    # For each n, we start with the largest x that could reasonably produce a 9-digit result
    for n, x in ((2, 9876),  # For n=2, x can be up to 4 digits (9876 is close to the 5-digit boundary)
                 (3, 987),   # For n=3, x can be up to 3 digits
                 (4, 98),    # For n=4, x can be up to 2 digits
                 (5, 9),     # For n=5 and above, x must be a single digit
                 (6, 9),
                 (7, 9),
                 (8, 9),
                 (9, 9)):

        # Start from the maximum x and work downward
        while x > 0:
            # Concatenate the products of x with the sequence (1,2,...,n)
            number = ''.join([str(i * x) for i in range(1, n + 1)])

            # Check if the result is a 9-digit 1-9 pandigital
            if len(number) == 9 and not any(d not in number for d in '123456789'):
                result = max(result, int(number))
                break  # Found the largest for this n, move to the next n

            x -= 1  # Try a smaller x

    return result


solution = cast(SolutionProtocol, largest_pan_digital_multiple)

solution.__doc__ = textwrap.dedent(r'''
Solution to Project Euler problem 38: Pandigital Multiples
https://projecteuler.net/problem=38

Problem Description:
Take the number 192 and multiply it by each of 1, 2, and 3:
192 × 1 = 192
192 × 2 = 384
192 × 3 = 576
By concatenating each product we get the 1 to 9 pandigital, 192384576.
We will call 192384576 the concatenated product of 192 and (1,2,3).

The same can be achieved by starting with 9 and multiplying by 1, 2, 3, 4, and 5, giving the pandigital, 918273645,
which is the concatenated product of 9 and (1,2,3,4,5).

What is the largest 1 to 9 pandigital 9-digit number that can be formed as the concatenated product of an integer
with (1,2, ..., n) where n > 1?

Solution Approach:
1. Search for numbers x that, when multiplied by consecutive integers starting from 1,
   produce a concatenated product that is a 9-digit pandigital number
2. Consider different sequence lengths (n) from 2 to 9
3. For each n, determine the maximum possible starting number x that could produce a 9-digit result
4. Search downward from this maximum to find pandigital concatenated products
5. Keep track of the largest pandigital number found

Algorithm Details:
- For n=2: We need x such that concatenating x×1 and x×2 gives 9 digits
  - This means x can have at most 4 digits (9876 × 1 = 9876, 9876 × 2 = 19752, concatenated: 987619752)
- For n=3: x can have at most 3 digits
- For n=4: x can have at most 2 digits
- For n=5 and above: x must be a single digit

For each combination of n and x, we:
1. Calculate the products x×1, x×2, ..., x×n
2. Concatenate these products into a single string
3. Check if the result is exactly 9 digits and contains each digit from 1 to 9 exactly once
4. If valid, compare with the current maximum and update if larger

Optimizations:
- Start with the largest possible x for each n since we want the maximum pandigital
- Break early once a valid pandigital is found for each n (since we're working in descending order)
- Use efficient string operations for concatenation and digit checking

Mathematical Insights:
- For a concatenated product to be exactly 9 digits, x and n must satisfy certain constraints
- For the result to be the largest possible, x should be as large as possible
- For a fixed n, a larger x will generally produce a larger concatenated product
- The largest pandigital will likely start with 9, which constrains our search space

Example Calculations:
- For x=192, n=3: 192×1 = 192, 192×2 = 384, 192×3 = 576, concatenated: 192384576 (pandigital)
- For x=9, n=5: 9×1 = 9, 9×2 = 18, 9×3 = 27, 9×4 = 36, 9×5 = 45, concatenated: 918273645 (pandigital)
- For x=9327, n=2: 9327×1 = 9327, 9327×2 = 18654, concatenated: 932718654 (pandigital)

The answer is 932718654, which is the concatenated product of 9327 and (1,2).
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
