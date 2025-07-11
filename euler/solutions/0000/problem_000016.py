# !/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
Solution to Project Euler problem 16: Power Digit Sum

Problem Statement:
2¹⁵ = 32768 and the sum of its digits is 3 + 2 + 7 + 6 + 8 = 26.
What is the sum of the digits of the number 2¹⁰⁰⁰?

Solution Approach:
This problem examines the behavior of digits in very large powers. The approach is straightforward
but relies on a programming language's ability to handle arbitrary-precision arithmetic:

1. Calculation of Large Number: We need to compute 2¹⁰⁰⁰, which is a 302-digit number that would
   cause overflow in languages with fixed-size integer types. Python naturally handles
   arbitrary-precision integers, making the calculation simple.

2. Digit Extraction: Once we have the large number, we convert it to a string and iterate
   through each character (digit) to compute the sum.

3. Generalization: While the original problem asks about 2¹⁰⁰⁰, our solution is generalized to
   handle any base and power, making it more versatile for similar problems.

The algorithm has a time complexity of O(log₁₀(base^power)), which is approximately
O(power·log₁₀(base)) - the number of digits in the result. The space complexity follows
the same pattern.

Python's ability to handle arbitrary-precision integers makes this problem trivial compared
to implementing it in languages that would require custom big integer libraries.

Test Cases:
- For power=15: Sum of digits in 2¹⁵ = 26
- For power=1000: Sum of digits in 2¹⁰⁰⁰ = 1366

URL: https://projecteuler.net/problem=16
Answer: 1366
"""

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol

problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={'power': 15}, answer=26,),
    ProblemArgs(kwargs={'power': 1000}, answer=1366,),
]


def solution(*, power: int, base: int = 2) -> int:
    """Calculate the sum of digits in the number base^power.

    This function computes the sum of individual digits in the number resulting from
    raising 'base' to the power of 'power'. The solution leverages Python's built-in
    support for arbitrary-precision integers, which automatically handles large numbers
    without overflow issues.

    Implementation Details:
    1. Calculate base^power using Python's exponentiation operator (**)
    2. Convert the result to a string to access individual digits
    3. Iterate through each character, convert back to integer, and sum

    The algorithm's efficiency depends on Python's internal implementation of large
    integer arithmetic and string conversion, but is generally very fast even for
    large powers.

    Args:
        power: The exponent to which the base is raised
        base: The base number to be raised to the specified power (default: 2)

    Returns:
        The sum of all individual digits in the resulting number

    Complexity:
        Time: O(log₁₀(base^power)) - proportional to the number of digits
        Space: O(log₁₀(base^power)) - for storing the string representation

    Examples:
        >>> solution(power=15)  # 2^15 = 32768
        26  # 3+2+7+6+8 = 26

        >>> solution(power=10, base=10)  # 10^10 = 10,000,000,000
        1  # Only one non-zero digit: 1+0+...+0 = 1
    """
    return sum(int(i) for i in str(base ** power))


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
