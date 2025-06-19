#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 48
# https://projecteuler.net/problem=48
# Answer: 9110846700
# Notes: 
"""
Solution to Project Euler problem 48: Self Powers.

This module calculates the last ten digits of the series 1¹ + 2² + 3³ + ... + n^n for
different values of n. The problem focuses on modular arithmetic and efficient computation
of large powers.

The solution leverages Python's built-in arbitrary-precision integer arithmetic to directly
compute the sum of self powers (i^i), followed by modulo 10^10 to extract just the last
ten digits. This approach is both elegant and efficient for the given constraints.

Key concepts:
- Modular arithmetic for handling large numbers
- Self powers (numbers raised to themselves)
- Python's efficient handling of arbitrary-precision integers
- Generator expressions for memory-efficient iteration
"""
import textwrap

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol

# Test cases for different upper limits of the series
# Each case computes the last 10 digits of the sum of self-powers up to n
problem_args_list: ProblemArgsList = [
    ProblemArgs(
        kwargs={'n': 10},      # Calculate the sum of self-powers from 1¹ to 10¹⁰
        answer=405071317,      # Last 10 digits of 10,405,071,317
    ),
    ProblemArgs(
        kwargs={'n': 100},     # Calculate the sum of self-powers from 1¹ to 100¹⁰⁰
        answer=9027641920,     # Last 10 digits of the result
    ),
    ProblemArgs(
        kwargs={'n': 1000},    # The main problem: sum from 1¹ to 1000¹⁰⁰⁰
        answer=9110846700,     # Last 10 digits of the result
    ),
    ProblemArgs(
        kwargs={'n': 10000},   # Extended test case for even larger series
        answer=6237204500,     # Last 10 digits of the result
    ),
]


def solution(*, n: int) -> int:
    """
    Calculate the last ten digits of the sum of self-powers series up to n.

    This function computes the sum of the series 1¹ + 2² + 3³ + ... + n^n and returns
    only the last ten digits of the result by performing modulo 10^10 on the final sum.

    The implementation leverages Python's built-in support for arbitrary-precision integers,
    which efficiently handles very large numbers without overflow. The generator expression
    approach ensures memory efficiency by computing each term on-the-fly rather than storing
    all terms in memory.

    Mathematical note: For large n, the values in the series grow extremely quickly. For example,
    1000^1000 has approximately 3000 digits. However, since we only need the last 10 digits,
    we can apply the modulo at the end of the calculation.

    Args:
        n: The upper limit of the series (inclusive)

    Returns:
        The last ten digits of the sum of the self-powers series

    Examples:
        >>> solution(n=10)
        405,071,317 # Last 10 digits of 10,405,071,317
        >>> solution(n=1000)
        9110846700 # Last 10 digits of the sum from 1¹ to 1000¹⁰⁰⁰
    """
    return sum(i ** i for i in range(1, n + 1)) % 10000000000


# Explicitly annotate that this function implements SolutionProtocol
solution: SolutionProtocol

solution.__doc__ = textwrap.dedent(r'''
solution to Project Euler problem 48: Self Powers
https://projecteuler.net/problem=48

Problem Description:
The series, 1^1 + 2^2 + 3^3 + ... + 10^{10} = 10405071317.
Find the last ten digits of the series, 1^1 + 2^2 + 3^3 + ... + 1000^{1000}.

Approach:
1. Direct Computation with Modular Arithmetic:
   - Calculate each term i^i directly using Python's efficient integer exponentiation
   - Sum all terms from i=1 to i=n
   - Apply modulo 10^10 to extract just the last 10 digits

2. Implementation Benefits:
   - Uses Python's built-in arbitrary-precision integers which handle the large numbers efficiently
   - Employs a generator expression for memory efficiency
   - Takes advantage of Python's optimized pow() function (used internally for **)

3. Mathematical Properties Utilized:
   - Modular arithmetic: (a + b) mod m = ((a mod m) + (b mod m)) mod m
   - This means we could also apply the modulo to each term before summing
   - However, Python's integer arithmetic is efficient enough that this optimization isn't necessary
     for the given constraints (n ≤ 10000)

4. Performance Considerations:
   - For very large values of n or in memory-constrained environments, an alternative approach
     would be to track only the last 10 digits during the calculation:
     ```python
     result = 0
     for i in range(1, n + 1):
         # Calculate i^i mod 10^10 efficiently
         term = pow(i, i, 10000000000)
         result = (result + term) % 10000000000
     return result
     ```
   - This would be more efficient for extremely large values of n

Algorithm Analysis:
- Time Complexity: O(n log n) where log n represents the complexity of raising a number to
  a power approximately the size of the number itself
- Space Complexity: O(1) as we only store the running sum regardless of input size

Note on the Results:
- For n=10: The last 10 digits are 405071317 (from 10405071317)
- For n=100: The last 10 digits are 9027641920
- For n=1000: The last 10 digits are 9110846700 (the answer to the main problem)
- For n=10000: The last 10 digits are 6237204500

The pattern of these last 10 digits doesn't follow an obvious progression, demonstrating
the chaotic nature of this sequence even when looking only at the last 10 digits.
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
