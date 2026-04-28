#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Migrated from
    euler_solver/solutions/solutions_0001_0100/solution_0095/p0095.py :: solve_amicable_chains_p0095_s0.

Project Euler Problem 95: Amicable Chains.

Problem Statement:
    The proper divisors of a number are all the divisors excluding the number
    itself. For example, the proper divisors of 28 are 1, 2, 4, 7, and 14. As
    the sum of these divisors is equal to 28, we call it a perfect number.

    Interestingly the sum of the proper divisors of 220 is 284 and the sum of
    the proper divisors of 284 is 220, forming a chain of two numbers. For this
    reason, 220 and 284 are called an amicable pair.

    Perhaps less well known are longer chains. For example, starting with 12496,
    we form a chain of five numbers:
    12496 -> 14288 -> 15472 -> 14536 -> 14264 (-> 12496 -> ...)

    Since this chain returns to its starting point, it is called an amicable
    chain.

    Find the smallest member of the longest amicable chain with no element
    exceeding one million.

Solution Approach:
    Use number theory for divisor summation and graph search (cycle detection)
    across chains formed by summing proper divisors. Efficiently sieve and
    cache divisor sums up to one million. Track visited nodes to avoid repeats.
    Expect O(N log N) complexity due to divisor sum calculations and chain
    traversals.

Answer: 14316
URL: https://projecteuler.net/problem=95"""
from __future__ import annotations

import sys
from typing import Dict, List


def show_solution() -> bool:
    return '--show' in sys.argv


def longest_amicable_chain(max_num: int) -> tuple[int, int]:
    divisor_sum: List[int] = [0] * (max_num + 1)
    for i in range(1, max_num // 2 + 1):
        for j in range(i * 2, max_num + 1, i):
            divisor_sum[j] += i
    smallest_member, longest_length = (0, 0)
    seen: Dict[int, int] = {}
    for i in range(1, max_num + 1):
        if i not in seen:
            ch, c, path = ({i}, divisor_sum[i], [i])
            while i <= c <= max_num and c not in ch:
                ch.add(c)
                path.append(c)
                c = divisor_sum[c]
            if c == i:
                if (len_ch := len(ch)) > longest_length:
                    longest_length, smallest_member = (len_ch, i)
                for x in path:
                    seen[x] = len_ch
    return (longest_length, smallest_member)


def solve(*, max_num: int) -> int:
    longest_length, smallest_member = longest_amicable_chain(max_num)
    if show_solution():
        print(f'Smallest Member of longest chain of length longest_length={longest_length!r} '
              f'is smallest_member={smallest_member!r}',
              file=sys.stderr)
    return smallest_member


if __name__ == '__main__':
    print(solve(max_num=int(sys.argv[1])))
