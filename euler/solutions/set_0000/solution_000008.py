#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r""" Solution to Project Euler problem 8: largest_product_in_a_series

Problem Statement:
  The four adjacent digits in the 1000-digit number that have the greatest product
  are 9 * 9 * 8 * 9 = 5832.  73167176531330624919225119674426574742355349194934
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
  71636269561882670428252483600823257530420752963450 Find the thirteen adjacent
  digits in the 1000-digit number that have the greatest product. What is the
  value of this product?

Solution Approach:
  Document the mathematical approach here.

URL: https://projecteuler.net/problem=8
Answer: None
"""
from __future__ import annotations

from functools import reduce

from euler.evaluator import evaluate_solutions, register_solution
from euler.setup import TestCase

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

test_cases: list[TestCase] = [
    TestCase(
        answer=5832,
        is_main_case=False,
        kwargs={'length': 4},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=23514624000,
        is_main_case=False,
        kwargs={'length': 13},
        solution_execution_time=None,
        solved=False
    ),
]


# Register this function as a solution for problem #8
@register_solution(problem_number=8, test_cases=test_cases)
def largest_product_in_a_series(*, length: int) -> int:
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
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(8))
