#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 74: Digit Factorial Chains.

Problem Statement:
    The number 145 is well known for the property that the sum of the factorial of its digits
    is equal to 145:
        1! + 4! + 5! = 1 + 24 + 120 = 145.

    Perhaps less well known is 169, in that it produces the longest chain of numbers that link
    back to 169; it turns out that there are only three such loops that exist:
        169 -> 363601 -> 1454 -> 169
        871 -> 45361 -> 871
        872 -> 45362 -> 872

    It is not difficult to prove that EVERY starting number will eventually get stuck in a loop.
    For example:
        69 -> 363600 -> 1454 -> 169 -> 363601 (-> 1454)
        78 -> 45360 -> 871 -> 45361 (-> 871)
        540 -> 145 (-> 145)

    Starting with 69 produces a chain of five non-repeating terms, but the longest non-repeating
    chain with a starting number below one million is sixty terms.

    How many chains, with a starting number below one million, contain exactly sixty non-repeating terms?

Solution Approach:
    Use memoization to store chain lengths for numbers to avoid recomputation.
    Precompute factorials of digits 0-9 for fast lookup.
    For each starting number below one million, generate the digit factorial sum chain until
    a loop or repetition is detected.
    Count chains with exactly 60 non-repeating terms.
    The solution involves efficient simulation and caching for performance (O(n) expected).
    Number theory and combinatorics help to identify repeated loops and avoid redundant calculations.

Answer: ...
URL: https://projecteuler.net/problem=74
"""
from __future__ import annotations

from typing import Any

from euler_solver.c_libs import use_wrapped_c_function
from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution, show_solution
from euler_solver.utils.color_codes import Color

euler_problem: int = 74
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_num': 10}},
    {'category': 'dev', 'input': {'max_num': 100}},
    {'category': 'dev', 'input': {'max_num': 1_000}},
    {'category': 'dev', 'input': {'max_num': 10_000}},
    {'category': 'dev', 'input': {'max_num': 100_000}},
    {'category': 'main', 'input': {'max_num': 1_000_000}},
    {'category': 'extra', 'input': {'max_num': 5_000_000}},
    {'category': 'extra', 'input': {'max_num': 10_000_000}},
]

# Precompute factorials of digits 0-9 for fast lookup
digit_factorials: tuple[int, ...] = (1, 1, 2, 6, 24, 120, 720, 5040, 40320, 362880,)


def sum_of_digit_factorials(n: int) -> int: ...

@use_wrapped_c_function('p0074')
def find_max_length_chains_digit_factorial(max_num: int) -> tuple[int, int]: ...

@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_digit_factorial_chains_p0074_s0(*, max_num: int) -> int: ...

Chains = dict[int, list[int]]


def add_chains(chains: Chains, number: int) -> bool: ...

def get_chain(max_num: int) -> Chains: ...

def print_chains(chains: Chains) -> None: ...

@use_wrapped_c_function('p0074')
def count_chains_with_max_length_digit_factorial(max_num: int) -> tuple[int, int]: ...

@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_digit_factorial_chains_p0074_s1(*, max_num: int) -> int: ...

@register_solution(euler_problem=euler_problem, max_test_case_index=5)
def solve_digit_factorial_chains_p0074_s2(*, max_num: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))
