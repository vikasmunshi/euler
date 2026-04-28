#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Migrated from
    euler_solver/solutions/solutions_0001_0100/solution_0046/p0046.py :: solve_goldbachs_other_conjecture_p0046_s0.

Project Euler Problem 46: Goldbach's Other Conjecture.

Problem Statement:
    It was proposed by Christian Goldbach that every odd composite number can be
    written as the sum of a prime and twice a square.

    9 = 7 + 2 x 1^2
    15 = 7 + 2 x 2^2
    21 = 3 + 2 x 3^2
    25 = 7 + 2 x 3^2
    27 = 19 + 2 x 2^2
    33 = 31 + 2 x 1^2

    It turns out that the conjecture was false.

    What is the smallest odd composite that cannot be written as the sum of a prime
    and twice a square?

Solution Approach:
    Use number theory and prime checking. Generate odd composites and verify if they
    can be expressed as prime + 2 * (square). Use efficient prime generation/check
    and iterate over squares. Expected complexity is moderate due to simple checks.

Answer: 5777
URL: https://projecteuler.net/problem=46"""
from __future__ import annotations

from typing import Dict, List, Set


def solve() -> int:
    primes: Set[int] = set()
    known_composites: Dict[int, List[int]] = dict()
    current_number = 2
    while True:
        if current_number not in known_composites:
            primes.add(current_number)
            known_composites[current_number ** 2] = [current_number]
        else:
            if current_number % 2 != 0:
                if not any((((current_number - p) / 2) ** 0.5 % 1 == 0 for p in primes if current_number > p != 2)):
                    return current_number
            for p in known_composites[current_number]:
                known_composites.setdefault(p + current_number, []).append(p)
            del known_composites[current_number]
        current_number += 1


if __name__ == '__main__':
    print(solve())
