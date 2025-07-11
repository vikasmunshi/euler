# !/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
Solution to Project Euler problem 8: Largest Product in a Series

Problem Statement:
The four adjacent digits in the 1000-digit number that have the greatest product are 9 × 9 × 8 × 9 = 5832.

73167176531330624919225119674426574742355349194934
96983520312774506326239578318016984801869478851843
85861560789112949495459501737958331952853208805511
12540698747158523863050715693290963295227443043557
66896648950445244523161731856403098711121722383113
62229893423380308135336276614282806444486645238749
30358907296290491560440772390713810515859307960866
70172427121883998797908792274921901699720888093776
65727333001053367881220235421809751254540594752243
52584907711670556013604839586446706324415722155397
53697817977846174064955149290862569321978468622482
83972241375657056057490261407972968652414535100474
82166370484403199890008895243450658541227588666881
16427171479924442928230863465674813919123162824586
17866458359124566529476545682848912883142607690042
24219022671055626321111109370544217506941658960408
07198403850962455444362981230987879927244284909188
84580156166097919133875499200524063689912560717606
05886116467109405077541002256983155200055935729725
71636269561882670428252483600823257530420752963450

Find the thirteen adjacent digits in the 1000-digit number that have the greatest product. 
What is the value of this product?

Solution Approach:
This solution employs a sliding window approach to find the maximum product of adjacent digits:

1. Sliding Window: We iterate through the 1000-digit number using a window of the specified length,
   extracting all possible subsequences.

2. Functional Programming: We use Python's functional programming tools (list comprehensions and
   reduce) to concisely express the algorithm.

3. Early Optimization: The solution could be optimized to skip windows containing zeros, as any
   product with a zero will be zero. However, the current implementation has a bug in this logic
   that needs to be fixed.

4. Generalization: The solution is parameterized by the window length, making it adaptable to
   different requirements (e.g., finding the product of 4 vs. 13 adjacent digits).

The algorithm has a time complexity of O(n), where n is the length of the number string, as
we process each possible window exactly once.

Test Cases:
- For length=4: 5832 (corresponding to the digits 9×9×8×9)
- For length=13: 23514624000 (corresponding to the 13 digits with maximum product)

URL: https://projecteuler.net/problem=8
Answer: 23514624000
"""
from functools import reduce

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol

problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={'length': 4}, answer=5832, ),  # Find the product of 4 adjacent digits - 5832
    ProblemArgs(kwargs={'length': 13}, answer=23514624000, ),  # Find the product of 13 adjacent digits - 23,514,624,000
]

# The 1000-digit number from the problem statement
number = '73167176531330624919225119674426574742355349194934' \
         '96983520312774506326239578318016984801869478851843' \
         '85861560789112949495459501737958331952853208805511' \
         '12540698747158523863050715693290963295227443043557' \
         '66896648950445244523161731856403098711121722383113' \
         '62229893423380308135336276614282806444486645238749' \
         '30358907296290491560440772390713810515859307960866' \
         '70172427121883998797908792274921901699720888093776' \
         '65727333001053367881220235421809751254540594752243' \
         '52584907711670556013604839586446706324415722155397' \
         '53697817977846174064955149290862569321978468622482' \
         '83972241375657056057490261407972968652414535100474' \
         '82166370484403199890008895243450658541227588666881' \
         '16427171479924442928230863465674813919123162824586' \
         '17866458359124566529476545682848912883142607690042' \
         '24219022671055626321111109370544217506941658960408' \
         '07198403850962455444362981230987879927244284909188' \
         '84580156166097919133875499200524063689912560717606' \
         '05886116467109405077541002256983155200055935729725' \
         '71636269561882670428252483600823257530420752963450'


def solution(*, length: int) -> int:
    """
    Find the greatest product of a sequence of adjacent digits in the 1000-digit number.

    Args:
        length (int): The number of adjacent digits to consider for the product

    Returns:
        int: The maximum product found among all possible subsequences of the given length

    Algorithm:
    1. Generate all possible subsequences of the specified length from the 1000-digit number
    2. Filter out subsequences containing the digit '0' (as their product would be zero)
    3. For each remaining subsequence, calculate the product of all its digits
    4. Return the maximum product found
    """
    return max([reduce(lambda a, b: int(a) * int(b), sequence)  # type: ignore
                for sequence in (number[i:i + length]
                                 for i in range(len(number) - length + 1)) if '0' not in sequence])


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
