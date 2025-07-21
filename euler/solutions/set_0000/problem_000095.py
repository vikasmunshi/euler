#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
Solution to Project Euler problem 95:

Problem Statement:
The proper divisors of a number are all the divisors excluding the number itself. For example, the proper divisors of
28 are 1, 2, 4, 7, and 14.  As the sum of these divisors is equal to 28, we call it a perfect number.

Interestingly the sum of the proper divisors of 220 is 284 and the sum of the proper divisors of 284 is 220,
forming a chain of two numbers. For this reason, 220 and 284 are called an amicable pair.

Perhaps less well known are longer chains. For example, starting with 12496, we form a chain of five numbers:
12496 -> 14288 -> 15472 -> 14536 -> 14264 (-> 12496 -> ·s)

Since this chain returns to its starting point, it is called an amicable chain.

Find the smallest member of the longest amicable chain with no element exceeding one million.

Solution Approach:
To solve this problem, we need to:
1. Calculate the sum of proper divisors for all numbers up to 1 million
2. For each number, follow the chain of sums until we either:
   - Return to the starting number (forming an amicable chain)
   - Encounter a number already in the current chain (creating a cycle that doesn't include the start)
   - Encounter a number greater than our limit
   - Encounter a number we've seen in a previous complete chain
3. Track the longest chain found, and return the smallest member of that chain

For efficient calculation of divisor sums, we use a sieve-like approach. For each number i,
we mark it as a divisor of all its multiples. This builds up the sum of proper divisors
for all numbers in one pass.

We then trace chains for each number, storing all numbers in each complete chain in a
'seen' dictionary to avoid recalculating chains.

Test Cases:
For a maximum number of 1,000,000, the smallest member of the longest amicable chain is 14316.

URL: https://projecteuler.net/problem=95
Answer: 14316
"""
from typing import Dict, List

from euler.evaluator import evaluate_solutions, register_solution
from euler.types import ProblemArgs, ProblemArgsList

# The problem number from Project Euler (https://projecteuler.net/problem=95)
problem_number: int = 95

# Define the test cases for validating the solution
problem_args_list: ProblemArgsList = [ProblemArgs(kwargs={'max_num': 10 ** 6}, answer=14316, ), ]


# Register this function as a solution for problem #95 with test cases
@register_solution(problem_number=problem_number, args_list=problem_args_list)
def longest_amicable_chain(*, max_num: int) -> int:
    """
    Find the smallest member of the longest amicable chain with no element exceeding max_num.

    An amicable chain is a sequence of numbers where each number is the sum of the proper
    divisors of the previous number, and the sequence eventually returns to the starting number.

    Args:
        max_num: The maximum value any number in the chain can have (1,000,000 for the problem)

    Returns:
        The smallest member of the longest amicable chain

    Algorithm:
        1. Calculate the sum of proper divisors for all numbers up to max_num using a sieve approach
        2. For each number, follow its chain until we either form a cycle or exceed max_num
        3. If we form a cycle that returns to the starting number, check if it's the longest so far
        4. Track numbers we've already processed to avoid redundant calculations
    """
    # Calculate sum of proper divisors for all numbers up to max_num
    divisor_sum: List[int] = [0] * (max_num + 1)
    for i in range(1, max_num // 2 + 1):
        for j in range(i * 2, max_num + 1, i):
            divisor_sum[j] += i

    ans, longest = 0, 0  # Track smallest member and length of longest chain
    seen: Dict[int, int] = {}  # Maps numbers to lengths of their chains

    for i in range(1, max_num + 1):
        if i not in seen:
            ch, c, path = {i}, divisor_sum[i], [i]  # Current chain set, current number, and path list

            # Follow the chain until we form a cycle or exceed max_num
            while i <= c <= max_num and c not in ch:
                ch.add(c)
                path.append(c)
                c = divisor_sum[c]  # Next number is sum of proper divisors

            # If we formed a proper amicable chain (cycle returns to start)
            if c == i:
                if (len_ch := len(ch)) > longest:  # Check if this is the longest chain so far
                    longest, ans = len_ch, i

                # Mark all numbers in the chain as processed
                for x in path:
                    seen[x] = len_ch

    return ans


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(problem_number))
