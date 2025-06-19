#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 34
# https://projecteuler.net/problem=34
# Answer: 40730
# Notes: 
import textwrap
from itertools import combinations_with_replacement

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol

problem_args_list: ProblemArgsList = [
    ProblemArgs(
        kwargs={},
        answer=40730,
    ),
]


def solution() -> int:
    """Find the sum of all numbers equal to the sum of the factorials of their digits.

    This function searches for numbers (like 145 = 1! + 4! + 5!) where the sum of the
    factorials of the digits equals the number itself. As specified in the problem,
    1 and 2 are excluded since they're not considered sums.

    Algorithm:
    1. Set an upper bound of 7 digits based on mathematical analysis:
       - For a d-digit number, the maximum sum of digit factorials is d×9! = d×362880
       - For d ≥ 8, any d-digit number must exceed this sum (10^7 > 8×9!)
       - Therefore, we only need to check numbers up to 7 digits

    2. For each possible number of digits (2 to 7):
       a. Generate all possible multisets of digits using combinations_with_replacement
       b. Calculate the sum of factorials for each multiset
       c. Check if this sum has the same number of digits as the original multiset
       d. Verify that all original digits appear in the sum (may be in different order)
       e. Confirm that the sum of factorials of the digits in the result equals the result itself

    3. Sum all valid numbers that meet these criteria

    Returns:
        The sum of all numbers that equal the sum of the factorials of their digits
    """
    upper_bound_num_digits = 7
    factorial = {'0': 1, '1': 1, '2': 2, '3': 6, '4': 24, '5': 120, '6': 720, '7': 5040, '8': 40320, '9': 362880}
    return sum(
        int(num)
        for num_digits in range(2, upper_bound_num_digits + 1)
        for digits in combinations_with_replacement('0123456789', num_digits)
        for num in (str(sum(factorial[d] for d in digits)),)
        if len(num) == num_digits
        and all(digit in num for digit in digits)
        and num == str(sum(factorial[n] for n in num))
    )


# Explicitly annotate that this function implements SolutionProtocol
solution: SolutionProtocol

solution.__doc__ = textwrap.dedent(r'''
Solution to Project Euler problem 34: Digit Factorials
https://projecteuler.net/problem=34

Problem Description:
145 is a curious number, as 1! + 4! + 5! = 1 + 24 + 120 = 145.
Find the sum of all numbers which are equal to the sum of the factorial of their digits.
Note: As 1! = 1 and 2! = 2 are not sums they are not included.

Solution Approach:
1. Mathematical Analysis for Upper Bound:
   - For a d-digit number, the maximum possible value is 10^d - 1
   - The maximum sum of factorials for d digits is d × 9! = d × 362,880
   - For any d-digit number to equal its digit factorial sum, we need: 10^(d-1) ≤ d × 9! < 10^d
   - Solving this inequality:
     * For d = 7: 10^6 (1,000,000) ≤ 7 × 9! (2,540,160) < 10^7 (10,000,000) ✓
     * For d = 8: 10^7 (10,000,000) ≤ 8 × 9! (2,903,040) < 10^8 (100,000,000) ✗
   - Therefore, we only need to check numbers with at most 7 digits

2. Optimization Strategy:
   - Rather than checking all numbers up to 2,540,160, we use a more efficient approach
   - We generate combinations of digits and check if their factorial sums form valid curious numbers
   - This drastically reduces the search space compared to a brute force approach
   - Key steps in the algorithm:
     a. Generate digit combinations of length 2 to 7
     b. Calculate factorial sums for each combination
     c. Verify if the sum has the same number of digits and contains the same digits
     d. Apply the final check to ensure the number equals its digit factorial sum

3. Implementation Notes:
   - We use combinations_with_replacement to generate all possible multisets of digits
   - The factorial values are precomputed for efficiency
   - The search constraints ensure we only consider valid curious numbers
   - The final verification confirms that each potential number truly equals its digit factorial sum

4. Results Analysis:
   - The algorithm finds exactly four curious numbers: 145, 40585, 1, and 2
   - As specified, we exclude 1 and 2 since they are not considered sums
   - The sum of the remaining curious numbers (145 + 40585) is 40730

This solution efficiently finds all numbers equal to the sum of their digit factorials by establishing a
mathematical upper bound and using combinatorial generation rather than brute force checking.
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
