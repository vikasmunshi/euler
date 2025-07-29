#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r""" Solution to Project Euler problem 74: digit_factorial_chains

Problem Statement:
  The number 145 is well known for the property that the sum of the factorial of
  its digits is equal to 145: 1! + 4! + 5! = 1 + 24 + 120 = 145. Perhaps less well
  known is 169, in that it produces the longest chain of numbers that link back to
  169; it turns out that there are only three such loops that exist: \begin{align}
  &169 \to 363601 \to 1454 \to 169\\ &871 \to 45361 \to 871\\ &872 \to 45362 \to
  872 \end{align} It is not difficult to prove that EVERY starting number will
  eventually get stuck in a loop. For example, \begin{align} &69 \to 363600 \to
  1454 \to 169 \to 363601 (\to 1454)\\ &78 \to 45360 \to 871 \to 45361 (\to 871)\\
  &540 \to 145 (\to 145) \end{align} Starting with 69 produces a chain of five
  non-repeating terms, but the longest non-repeating chain with a starting number
  below one million is sixty terms. How many chains, with a starting number below
  one million, contain exactly sixty non-repeating terms?

Solution Approach:
  Document the mathematical approach here.

URL: https://projecteuler.net/problem=74
Answer: None
"""
from __future__ import annotations

from collections import Counter
from functools import lru_cache
from math import factorial

from euler.evaluator import evaluate_solutions, register_solution, show_solution
from euler.setup import TestCase

test_cases: list[TestCase] = [
    TestCase(
        answer=[1, 36],
        is_main_case=False,
        kwargs={'max_num': 10},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=[2, 54],
        is_main_case=False,
        kwargs={'max_num': 100},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=[12, 55],
        is_main_case=False,
        kwargs={'max_num': 1000},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=[42, 60],
        is_main_case=False,
        kwargs={'max_num': 10000},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=[42, 60],
        is_main_case=False,
        kwargs={'max_num': 100000},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=[60, 402],
        is_main_case=False,
        kwargs={'max_num': 1000000},
        solution_execution_time=None,
        solved=False
    ),
]
# Dictionary mapping digit strings to their factorial values (0! to 9!)
# Used for quick lookup of digit factorials instead of recalculating
digit_factorials: dict[str, int] = {str(d): factorial(d) for d in range(0, 10)}


def sum_digit_factorial(n: int) -> int:
    """Calculate sum of factorials of digits in a number.

    Args:
        n: Input number whose digits' factorials will be summed

    Returns:
        Sum of factorials of individual digits
    """
    return sum(digit_factorials[d] for d in str(n))


@lru_cache(maxsize=None)
def chain_len(n: int) -> int:
    """Calculate length of non-repeating chain of digit factorial sums.

    All chains must eventually terminate in a loop because:
    1. For any n-digit number, the sum of digit factorials is at most n * 9! = n * 362880
    2. This means a number with n digits will produce a sum with at most log10(n * 362880) + 1 digits
    3. For any starting number, the number of digits in the chain will eventually decrease
    4. With a finite set of possible values, the chain must enter a loop

    Args:
        n: Starting number for the chain

    Returns:
        Length of non-repeating chain before a repeat occurs
    """
    num, chain = n, {n}
    while (num := sum_digit_factorial(num)) not in chain:
        chain.add(num)
    return len(chain)


# Register this function as a solution for problem #74
@register_solution(problem_number=74, test_cases=test_cases)
def digit_factorial_chains(*, max_num: int) -> list:
    """Find the maximum chain length and count of numbers producing that length.

    The function uses chain_len(sum_digit_factorial(n)) instead of chain_len(n) as an optimization.
    Since the first step in any chain is to calculate sum of digit factorials, many different numbers
    can lead to the same sum. By caching the chain length starting from the sum rather than the
    original number, we get more cache hits and avoid redundant calculations.

    Args:
        max_num: Upper limit of numbers to check

    Returns:
        Tuple containing (maximum chain length, count of numbers with that length)
    """
    chain_lengths = [1 if (n == (next_n := sum_digit_factorial(n))) else chain_len(next_n) + 1
                     for n in range(1, max_num + 1)]
    length_counts: Counter[int] = Counter(chain_lengths)
    if show_solution():
        print(f'Chain lengths for {max_num=}: {sorted(length_counts.items())}')
    return sorted(max(length_counts.items()))


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(74))
