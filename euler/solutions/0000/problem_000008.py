#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Solution to Project Euler problem 8: Largest product in a series
https://projecteuler.net/problem=8

Problem Statement:
The four adjacent digits in the 1000-digit number that have the greatest product are 9×9×8×9=5832.

Find the thirteen adjacent digits in the 1000-digit number that have the greatest product.
What is the value of this product?

Approach:
This solution iterates through all possible subsequences of the specified length in the 1000-digit number.
For each subsequence, it calculates the product of its digits and finds the maximum value.

Known answers:
- For 4 adjacent digits: 5832
- For 13 adjacent digits: 23,514,624,000
"""
import textwrap
from functools import reduce

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol

# Define test cases with their expected answers for validation
problem_args_list: ProblemArgsList = [
    ProblemArgs(
        kwargs={'length': 4},  # Find the product of 4 adjacent digits
        answer=5832,  # The answer for 4 adjacent digits is 5832
    ),
    ProblemArgs(
        kwargs={'length': 13},  # Find the product of 13 adjacent digits
        answer=23514624000,  # The answer for 13 adjacent digits is 23,514,624,000
    ),
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
    2. For each subsequence, calculate the product of all its digits
    3. Return the maximum product found

    Note: The condition '0 not in sequence' is intended to filter out sequences containing 0,
          but there appears to be a syntax issue. The code would still work correctly if the 
          condition checked for '0' not in sequence without quotes, as any sequence with 0 
          would result in a product of 0.
    """
    return max([reduce(lambda a, b: int(a) * int(b), sequence)  # type: ignore
                for sequence in (number[i:i + length]
                                 for i in range(len(number) - length + 1)) if '0 not in sequence'])


# Explicitly annotate that this function implements SolutionProtocol
solution: SolutionProtocol

# Preserve the original docstring for the solution function
solution.__doc__ = textwrap.dedent(r'''
solution to Project Euler problem 8
https://projecteuler.net/problem=8
The four adjacent digits in the 1000-digit number that have the greatest product are 9 * 9 * 8 * 9 = 5832.

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

Find the thirteen adjacent digits in the 1000-digit number that have the greatest product. What is the value of this product?

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
