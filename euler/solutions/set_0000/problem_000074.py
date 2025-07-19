# !/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
Solution to Project Euler problem 74:

Problem Statement:
The number 145 is well known for the property that the sum of the factorial of its digits is equal to 145:
1! + 4! + 5! = 1 + 24 + 120 = 145.

Perhaps less well known is 169, in that it produces the longest chain of numbers that link back to 169; it turns out
that there are only three such loops that exist:

169 -> 363601 -> 1454 -> 169
871 -> 45361 -> 871
872 -> 45362 -> 872

It is not difficult to prove that EVERY starting number will eventually get stuck in a loop. For example,

69 -> 363600 -> 1454 -> 169 -> 363601 -> (1454)
78 -> 45360 -> 871 -> 45361 -> (871)
540-> 145 -< (145)

Starting with 69 produces a chain of five non-repeating terms, but the longest non-repeating chain with a starting
number below one million is sixty terms.

How many chains, with a starting number below one million, contain exactly sixty non-repeating terms?

Solution Approach:
We use an optimized approach combining memoization and chain detection:
1. Pre-calculate factorials for digits 0-9 for quick lookup
2. For each number, track the chain of digit factorial sums using a set
3. Use @lru_cache decorator to memoize chain lengths and avoid recalculations
4. Optimize by caching chain lengths starting from the sum of digit factorials
5. Return both the maximum chain length and count of numbers producing that length

Test Cases and Expected Results:
- For max_num=10: Maximum chain length 36, found in 1 number
- For max_num=100: Maximum chain length 54, found in 2 numbers
- For max_num=1,000: Maximum chain length 55, found in 12 numbers
- For max_num=10,000: Maximum chain length 60, found in 42 numbers
- For max_num=100,000: Maximum chain length 60, found in 42 numbers
- For max_num=1,000,000: Maximum chain length 60, found in 402 numbers

URL: https://projecteuler.net/problem=74
Answer: 402
"""
from collections import Counter
from functools import lru_cache
from math import factorial
from operator import itemgetter
from typing import Dict, Tuple

from euler.evaluator import evaluate_solutions, register_solution, show_solution
from euler.types import ProblemArgs, ProblemArgsList

# The problem number from Project Euler (https://projecteuler.net/problem=74)
problem_number: int = 74

# Define the test cases for validating the solution
problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={'max_num': 10 ** 1, }, answer=(36, 1), ),
    ProblemArgs(kwargs={'max_num': 10 ** 2, }, answer=(54, 2), ),
    ProblemArgs(kwargs={'max_num': 10 ** 3, }, answer=(55, 12), ),
    ProblemArgs(kwargs={'max_num': 10 ** 4, }, answer=(60, 42), ),
    ProblemArgs(kwargs={'max_num': 10 ** 5, }, answer=(60, 42), ),
    ProblemArgs(kwargs={'max_num': 10 ** 6, }, answer=(60, 402), ),
]

# Dictionary mapping digit strings to their factorial values (0! to 9!)
# Used for quick lookup of digit factorials instead of recalculating
digit_factorials: Dict[str, int] = {str(d): factorial(d) for d in range(0, 10)}


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


# Register this function as a solution for problem #74 with test cases
@register_solution(problem_number=problem_number, args_list=problem_args_list)
def digit_factorial_non_repeating_chain_length(*, max_num: int) -> Tuple[int, int]:
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
    return max(length_counts.items(), key=itemgetter(0))


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(problem_number))
