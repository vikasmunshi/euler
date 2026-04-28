#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Migrated from
    euler_solver/solutions/solutions_0001_0100/solution_0060/p0060.py :: solve_prime_pair_sets_p0060_s0.

Project Euler Problem 60: Prime Pair Sets.

Problem Statement:
    The primes 3, 7, 109, and 673, are quite remarkable. By taking any two primes and
    concatenating them in any order the result will always be prime. For example, taking
    7 and 109, both 7109 and 1097 are prime. The sum of these four primes, 792,
    represents the lowest sum for a set of four primes with this property.

    Find the lowest sum for a set of five primes for which any two primes concatenate
    to produce another prime.

Solution Approach:
    Use number theory and graph search. Generate primes and build a graph where edges
    connect primes forming prime concatenations. Then search for a complete clique of
    size five. Employ primality tests for concatenated numbers efficiently.
    The approach may involve backtracking and caching primality results.

Answer: 26033
URL: https://projecteuler.net/problem=60"""
from __future__ import annotations

import sys
from functools import lru_cache
from itertools import combinations
from typing import Generator, List, Tuple


def is_prime(num: int) -> bool:
    if num < 2:
        return False
    if num == 2:
        return True
    if num % 2 == 0:
        return False
    i = 3
    while i * i <= num:
        if num % i == 0:
            return False
        i += 2
    return True


@lru_cache(maxsize=None)
def concatenate_is_prime(a: int, b: int) -> bool:
    return is_prime(int(str(a) + str(b))) and is_prime(int(str(b) + str(a)))


def print_solution(solution_list: List[int]) -> None:
    print(f'solution_list={solution_list!r}', file=sys.stderr, )
    for p1, p2 in combinations(solution_list, 2):
        print(f'concatenate_prime({p1}, {p2})={concatenate_is_prime(p1, p2)}', file=sys.stderr)


def solution_pairs(primes: Tuple[int, ...]) -> Generator[List[int], None, None]:
    for i, p1 in enumerate(primes):
        for p2 in primes[i + 1:]:
            if concatenate_is_prime(p1, p2):
                yield [p1, p2]


def show_solution() -> bool:
    return '--show' in sys.argv


def extend_solution(current_list: List[int], primes: Tuple[int, ...]) -> Generator[List[int], None, None]:
    for prime in primes:
        if prime <= current_list[-1]:
            continue
        for p in current_list:
            if not concatenate_is_prime(p, prime):
                break
        else:
            yield (current_list + [prime])


def primes_sundaram_sieve(max_num: int) -> tuple[int, ...]:
    if max_num < 2:
        return ()
    n = (max_num - 1) // 2
    marked = bytearray(n + 1)
    for i in range(1, n + 1):
        j = i
        while i + j + 2 * i * j <= n:
            marked[i + j + 2 * i * j] = 1
            j += 1
    primes = [2] if max_num >= 2 else []
    primes.extend((2 * i + 1 for i in range(1, n + 1) if not marked[i]))
    return tuple(primes)


def solve(*, set_length: int) -> int:
    primes = primes_sundaram_sieve(max_num=10 ** (set_length - 1))
    solution_generator = {3: (solution_3 for solution_2 in solution_pairs(primes=primes) for solution_3 in
                              extend_solution(current_list=solution_2, primes=primes)),
                          4: (solution_4 for solution_2 in solution_pairs(primes=primes) for solution_3 in
                              extend_solution(current_list=solution_2, primes=primes) for solution_4 in
                              extend_solution(current_list=solution_3, primes=primes)),
                          5: (solution_5 for solution_2 in solution_pairs(primes=primes) for solution_3 in
                              extend_solution(current_list=solution_2, primes=primes) for solution_4 in
                              extend_solution(current_list=solution_3, primes=primes) for solution_5 in
                              extend_solution(current_list=solution_4, primes=primes))}
    try:
        solution_list = next(solution_generator[set_length])
    except KeyError:
        raise OverflowError(f'No solution implemented for set_length={set_length!r}')
    except StopIteration:
        raise ValueError(f'No solution found for set_length={set_length!r} within max prime = {primes[-1]}')
    else:
        if show_solution():
            print(f'max prime = {primes[-1]} num_primes = {len(primes)}', file=sys.stderr, )
            print_solution(solution_list)
        return sum(solution_list)


if __name__ == '__main__':
    print(solve(set_length=int(sys.argv[1])))
