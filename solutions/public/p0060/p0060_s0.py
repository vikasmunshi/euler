#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 60: Prime Pair Sets [Level 3]. """
from __future__ import annotations

import functools
import itertools
import typing

from solver.runners import runner


def is_prime(num: int) -> bool:
    """Trial-division primality test up to sqrt(num); O(sqrt(num))."""
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


@functools.lru_cache(maxsize=None)
def concatenate_is_prime(a: int, b: int) -> bool:
    """Edge predicate: both concatenations a||b and b||a are prime; memoized across the search."""
    return is_prime(int(str(a) + str(b))) and is_prime(int(str(b) + str(a)))


def extend_solution(current_list: list[int], primes: tuple[int, ...]) -> typing.Generator[list[int], None, None]:
    """Yield each clique grown by one prime greater than the last that pairs with every member."""
    for prime in primes:
        if prime <= current_list[-1]:
            continue
        for p in current_list:
            if not concatenate_is_prime(p, prime):
                break
        else:
            yield (current_list + [prime])


def print_solution(solution_list: list[int]) -> None:
    """Print the clique and verify each pair concatenates to a prime (diagnostic --show output)."""
    print(f"solution_list={solution_list!r}")
    for p1, p2 in itertools.combinations(solution_list, 2):
        print(f"concatenate_prime({p1}, {p2})={concatenate_is_prime(p1, p2)}")


def primes_sundaram_sieve(max_num: int) -> tuple[int, ...]:
    """Sieve of Sundaram: primes up to max_num in ascending order; O(N log log N)."""
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


def solution_pairs(primes: tuple[int, ...]) -> typing.Generator[list[int], None, None]:
    """Yield every ascending prime pair forming an edge (both concatenations prime)."""
    for i, p1 in enumerate(primes):
        for p2 in primes[i + 1:]:
            if concatenate_is_prime(p1, p2):
                yield [p1, p2]


@runner.main
def solve(*args: str) -> str:
    """Find the minimum-sum clique of set_length primes (pairwise-concatenable) by lazy
    ascending-order DFS over nested generators; ascending order makes the first hit minimal.
    Every answer prime is below 10^(set_length-1), bounding the sieved candidate set."""
    set_length = runner.parse_int(args[0])

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
        if runner.show:
            print(f"max prime = {primes[-1]} num_primes = {len(primes)}")
            print_solution(solution_list)
        return str(sum(solution_list))


if __name__ == "__main__":
    raise SystemExit(solve())
