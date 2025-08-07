#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
  Project Euler Problem 95: Amicable Chains.

  Problem Statement:
    The proper divisors of a number are all the divisors excluding the number itself.
    For example, the proper divisors of 28 are 1, 2, 4, 7, and 14. As the sum of these
    divisors is equal to 28, we call it a perfect number.

    Interestingly the sum of the proper divisors of 220 is 284 and the sum of the proper
    divisors of 284 is 220, forming a chain of two numbers. For this reason, 220 and 284
    are called an amicable pair.

    Perhaps less well known are longer chains. For example, starting with 12496, we form
    a chain of five numbers:

    12496 -> 14288 -> 15472 -> 14536 -> 14264 (-> 12496 -> ...)

    Since this chain returns to its starting point, it is called an amicable chain.

    Find the smallest member of the longest amicable chain with no element exceeding one
    million.

  Solution Approach:
    To solve this problem, first understand the concept of proper divisors and
    how to efficiently compute their sums for numbers up to one million. Use a
    sieve-like method to precompute the sum of proper divisors for all numbers
    up to the limit.

    Then, for each number, attempt to build the amicable chain by repeatedly
    replacing the number with the sum of its proper divisors, tracking the
    chain to detect cycles. Find the longest chain that does not exceed the one
    million boundary.

    Finally, from these detected chains, determine the smallest member of the
    longest amicable chain. Efficient bookkeeping and cycle detection are key
    to handling this problem within a reasonable runtime.

  Test Cases:
    main:
      max_num=1000000,
      answer=14316.


  Answer: 14316
  URL: https://projecteuler.net/problem=95
"""
from __future__ import annotations

from typing import Dict, List

from euler.logger import logger
from euler.setup import TestCaseCategory, evaluate, register_solution


@register_solution(euler_problem=95, test_case_category=TestCaseCategory.EXTENDED)
def amicable_chains(*, max_num: int) -> int:
    divisor_sum: List[int] = [0] * (max_num + 1)
    for i in range(1, max_num // 2 + 1):
        for j in range(i * 2, max_num + 1, i):
            divisor_sum[j] += i
    ans, longest = (0, 0)
    seen: Dict[int, int] = {}
    for i in range(1, max_num + 1):
        if i not in seen:
            ch, c, path = ({i}, divisor_sum[i], [i])
            while i <= c <= max_num and c not in ch:
                ch.add(c)
                path.append(c)
                c = divisor_sum[c]
            if c == i:
                if (len_ch := len(ch)) > longest:
                    longest, ans = (len_ch, i)
                for x in path:
                    seen[x] = len_ch
    return ans


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=95, time_out_in_seconds=300, mode='evaluate'))
