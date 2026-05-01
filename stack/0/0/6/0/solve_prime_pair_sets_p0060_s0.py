#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Migrated from:
  file: euler_solver/solutions/solutions_0001_0100/solution_0060/p0060.py
  func: solve_prime_pair_sets_p0060_s0
"""

from __future__ import annotations

from functools import lru_cache
from itertools import combinations
from sys import argv
from typing import Generator, List, Tuple


def show_solution() -> bool:
    return "--show" in argv


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
    print(f"solution_list={solution_list!r}")
    for p1, p2 in combinations(solution_list, 2):
        print(f"concatenate_prime({p1}, {p2})={concatenate_is_prime(p1, p2)}")


def solution_pairs(primes: Tuple[int, ...]) -> Generator[List[int], None, None]:
    for i, p1 in enumerate(primes):
        for p2 in primes[i + 1:]:
            if concatenate_is_prime(p1, p2):
                yield [p1, p2]


def extend_solution(current_list: List[int], primes: Tuple[int, ...]) -> Generator[List[int], None, None]:
    for prime in primes:
        if prime <= current_list[-1]:
            continue
        for p in current_list:
            if not concatenate_is_prime(p, prime):
                break
        else:
            yield (current_list + [prime])


def solve(*, set_length: int) -> int:
    primes = primes_sundaram_sieve(max_num=10 ** (set_length - 1))
    solution_generator = {
        3: (
            solution_3
            for solution_2 in solution_pairs(primes=primes)
            for solution_3 in extend_solution(current_list=solution_2, primes=primes)
        ),
        4: (
            solution_4
            for solution_2 in solution_pairs(primes=primes)
            for solution_3 in extend_solution(current_list=solution_2, primes=primes)
            for solution_4 in extend_solution(current_list=solution_3, primes=primes)
        ),
        5: (
            solution_5
            for solution_2 in solution_pairs(primes=primes)
            for solution_3 in extend_solution(current_list=solution_2, primes=primes)
            for solution_4 in extend_solution(current_list=solution_3, primes=primes)
            for solution_5 in extend_solution(current_list=solution_4, primes=primes)
        ),
    }
    try:
        solution_list = next(solution_generator[set_length])
    except KeyError:
        raise OverflowError(f"No solution implemented for set_length={set_length!r}")
    except StopIteration:
        raise ValueError(f"No solution found for set_length={set_length!r} within max prime = {primes[-1]}")
    else:
        if show_solution():
            print(f"max prime = {primes[-1]} num_primes = {len(primes)}")
            print_solution(solution_list)
        return sum(solution_list)


def main() -> int:
    print(solve(set_length=int(argv[1])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
