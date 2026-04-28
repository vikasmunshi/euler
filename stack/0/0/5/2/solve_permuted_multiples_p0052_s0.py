#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Migrated from
    euler_solver/solutions/solutions_0001_0100/solution_0052/p0052.py :: solve_permuted_multiples_p0052_s0.

Project Euler Problem 52: Permuted Multiples.

Problem Statement:
    It can be seen that the number, 125874, and its double, 251748, contain exactly the
    same digits, but in a different order.

    Find the smallest positive integer, x, such that 2x, 3x, 4x, 5x, and 6x, contain the
    same digits.

Solution Approach:
    Use digit frequency comparison to check permutations for multiples 2x to 6x.
    Iterate over integers and test the condition by sorting digits or using count arrays.
    Efficient checks and early termination reduce complexity.

Answer: 142857
URL: https://projecteuler.net/problem=52"""
from __future__ import annotations


def solve(*, multiples: int) -> int:
    if not (isinstance(multiples, int) and 1 < multiples < 7):
        raise ValueError('multiples must be an integer between 2 and 6, both inclusive.')
    multiples_range = tuple(range(1, multiples + 1))
    for i in range(1, sys.maxsize // multiples):
        if len({''.join(sorted(str(i * multiple))) for multiple in multiples_range}) == 1:
            return i
    else:
        raise ValueError('No solution found')


if __name__ == '__main__':
    import sys

    print(solve(multiples=int(sys.argv[1])))
