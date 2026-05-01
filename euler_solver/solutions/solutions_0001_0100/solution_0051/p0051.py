#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 51: Prime Digit Replacements.

Problem Statement:
    By replacing the 1st digit of the 2-digit number *3, it turns out that six of the nine
    possible values: 13, 23, 43, 53, 73, and 83, are all prime.

    By replacing the 3rd and 4th digits of 56**3 with the same digit, this 5-digit number is
    the first example having seven primes among the ten generated numbers, yielding the family:
    56003, 56113, 56333, 56443, 56663, 56773, and 56993. Consequently 56003, being the first
    member of this family, is the smallest prime with this property.

    Find the smallest prime which, by replacing part of the number (not necessarily adjacent
    digits) with the same digit, is part of an eight prime value family.

Solution Approach:
    Use prime checking and efficient digit replacement patterns. Generate candidate primes and
    examine digit subsets for replacement to form families. Employ combinatorics on digit indices,
    prime sieves, and incremental search. Aim for pruning by early skips to handle large search
    efficiently.

Answer: 121313
URL: https://projecteuler.net/problem=51
"""
from __future__ import annotations

from typing import Any

from euler_solver.framework import evaluate, logger, register_solution
from euler_solver.lib_primes import is_prime, primes_sundaram_sieve

euler_problem: int = 51
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'num_digits': 6, 'prime_run': 6}, 'answer': 13},
    {'category': 'dev', 'input': {'num_digits': 6, 'prime_run': 7}, 'answer': 56003},
    {'category': 'main', 'input': {'num_digits': 6, 'prime_run': 8}, 'answer': 121313},
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_prime_digit_replacements_p0051_s0(*, num_digits: int, prime_run: int) -> int:
    for prime in primes_sundaram_sieve(10 ** num_digits):
        for replaced in '0123456789'[:10 - prime_run]:
            sequence = tuple((new_prime for replacement in '0123456789'
                              if replacement >= replaced
                              if (new_prime := int(str(prime).replace(replaced, replacement))) >= prime
                              and is_prime(new_prime)))
            if len(sequence) == prime_run:
                return prime
    else:
        raise ValueError('No solution found')


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
