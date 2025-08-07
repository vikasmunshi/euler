#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
  Project Euler Problem 60: Prime Pair Sets.

  Problem Statement:
    The primes 3, 7, 109, and 673, are quite remarkable. By taking any two
    primes and concatenating them in any order the result will always be
    prime. For example, taking 7 and 109, both 7109 and 1097 are prime. The
    sum of these four primes, 792, represents the lowest sum for a set of
    four primes with this property.

    Find the lowest sum for a set of five primes for which any two primes
    concatenate to produce another prime.

  Solution Approach:
    To solve this problem, consider checking combinations of primes and
    testing whether every pairwise concatenation forms a prime. A key
    approach involves generating primes efficiently using a sieve method
    and implementing a fast primality check for concatenated numbers.

    Construct a graph where each node is a prime and edges represent the
    concatenation primality property. Then search for complete subgraphs
    (cliques) of size five. Employ backtracking with pruning to limit the
    search space, starting from smaller sets that satisfy the property.

    Optimizing concatenation checks by caching results and avoiding
    redundant tests will help handle the computational intensity of the
    problem.

  Test Cases:
    preliminary:
      set_length=3,
      answer=107.

      set_length=4,
      answer=792.

    main:
      set_length=5,
      answer=26033.


  Answer: 26033
  URL: https://projecteuler.net/problem=60
"""
from __future__ import annotations

from itertools import combinations
from typing import Generator, List, Tuple

from euler.logger import logger
from euler.maths.primes import get_pre_computed_primes_sundaram_sieve, is_prime
from euler.setup import TestCaseCategory, evaluate, register_solution, show_solution


def concatenate_prime(a: int, b: int) -> bool:
    return is_prime(int(str(a) + str(b))) and is_prime(int(str(b) + str(a)))


def extend_solution(current_list: List[int], primes: Tuple[int, ...]) -> Generator[List[int], None, None]:
    for prime in primes:
        if prime <= current_list[-1]:
            continue
        if all((concatenate_prime(p, prime) for p in current_list)):
            yield (current_list + [prime])


def print_solution(solution_list: List[int]) -> None:
    print(f'solution_list={solution_list!r}')
    for p1, p2 in combinations(solution_list, 2):
        print(f'concatenate_prime({p1}, {p2})={concatenate_prime(p1, p2)}')


def solution_pairs(primes: Tuple[int, ...]) -> Generator[List[int], None, None]:
    for i, p1 in enumerate(primes):
        for p2 in primes[i + 1:]:
            if concatenate_prime(p1, p2):
                yield [p1, p2]


@register_solution(euler_problem=60, test_case_category=TestCaseCategory.EXTENDED)
def prime_pair_sets(*, set_length: int) -> int:
    primes: Tuple[int, ...] = (2, 3, 5, 7)
    for i in range(2, 5):
        primes = get_pre_computed_primes_sundaram_sieve(max_limit=10 ** (set_length - 1))
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
            continue
        else:
            if show_solution():
                print(f'max prime = {primes[-1]}')
                print_solution(solution_list)
            return sum(solution_list)
    else:
        raise ValueError(f'No solution found for set_length={set_length!r} within max prime = {primes[-1]}')


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=60, time_out_in_seconds=300, mode='evaluate'))
