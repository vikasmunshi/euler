#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 60: Prime Pair Sets [Level 3]. """
from __future__ import annotations

import functools
import itertools
import sys
import typing
from sys import argv, stderr
from time import perf_counter
from typing import Any


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


@functools.lru_cache(maxsize=None)
def concatenate_is_prime(a: int, b: int) -> bool:
    return is_prime(int(str(a) + str(b))) and is_prime(int(str(b) + str(a)))


def extend_solution(current_list: list[int], primes: tuple[int, ...]) -> typing.Generator[list[int], None, None]:
    for prime in primes:
        if prime <= current_list[-1]:
            continue
        for p in current_list:
            if not concatenate_is_prime(p, prime):
                break
        else:
            yield (current_list + [prime])


def print_solution(solution_list: list[int]) -> None:
    print(f"solution_list={solution_list!r}")
    for p1, p2 in itertools.combinations(solution_list, 2):
        print(f"concatenate_prime({p1}, {p2})={concatenate_is_prime(p1, p2)}")


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


def solution_pairs(primes: tuple[int, ...]) -> typing.Generator[list[int], None, None]:
    for i, p1 in enumerate(primes):
        for p2 in primes[i + 1:]:
            if concatenate_is_prime(p1, p2):
                yield [p1, p2]


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
        if sys.argv[-1] == "--show":
            print(f"max prime = {primes[-1]} num_primes = {len(primes)}")
            print_solution(solution_list)
        return sum(solution_list)


def main(**kwargs: Any) -> int:
    """
    Usage: ./file.py <kwarg>... [--runs=1] [--show]
    Output: "<runs> <avg_seconds> <result>"
    """
    try:
        runs_arg: str = next((arg for arg in argv[1:] if arg.startswith("--runs=")))
        runs: int = int(runs_arg.split("=", 1)[1])
        assert runs > 0
    except (AssertionError, StopIteration, ValueError):
        runs = 1
    elapsed: list[float] = []
    result: int | None = None
    rc: int = 0
    errors: list[str] = []
    for _ in range(runs):
        _start, _result, _stop = (perf_counter(), solve(**kwargs), perf_counter())
        elapsed.append(_stop - _start)
        if result is not None and _result != result:
            errors.append(f"Expected consistent result, got {_result} previous result={result}")
        result = _result
    if result is None:
        errors.append("Expected a result, got None")
    average: float = sum(elapsed) / len(elapsed)
    if errors:
        print("\n".join(errors), file=stderr)
        rc = 1
    print(f"{runs} {average} {result}")
    return rc


if __name__ == "__main__":
    raise SystemExit(main(set_length=int(argv[1])))
