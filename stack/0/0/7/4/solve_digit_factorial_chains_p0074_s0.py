#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Migrated from:
  file: euler_solver/solutions/solutions_0001_0100/solution_0074/p0074.py
  func: solve_digit_factorial_chains_p0074_s0
"""

from __future__ import annotations

from sys import argv

digit_factorials: tuple[int, ...] = (1, 1, 2, 6, 24, 120, 720, 5040, 40320, 362880)


def sum_of_digit_factorials(n: int) -> int:
    result = 0
    while n > 0:
        result += digit_factorials[n % 10]
        n //= 10
    return result


def find_max_length_chains_digit_factorial(max_num: int) -> tuple[int, int]:
    chain_length_cache: dict[int, int] = {}
    graph: dict[int, int] = {}
    max_chain_length: int = 0
    max_chain_length_count: int = 0
    for start in range(2, max_num + 1):
        seen: list[int] = []
        current: int = start
        while current not in seen and current not in chain_length_cache:
            seen.append(current)
            if current not in graph:
                graph[current] = sum_of_digit_factorials(current)
            current = graph[current]
        if current in chain_length_cache:
            length = len(seen) + chain_length_cache[current]
        else:
            length = len(seen)
        for i, num in enumerate(seen):
            chain_length_cache[num] = length - i
            graph[num] = seen[i + 1] if i + 1 < len(seen) else current
        if (chain_length := chain_length_cache[start]) > max_chain_length:
            max_chain_length = chain_length
            max_chain_length_count = 1
        elif chain_length == max_chain_length:
            max_chain_length_count += 1
    return (max_chain_length, max_chain_length_count)


def show_solution() -> bool:
    return "--show" in argv


def solve(*, max_num: int) -> int:
    max_chain_length, max_chain_length_count = find_max_length_chains_digit_factorial(max_num)
    if show_solution():
        print(
            f"max_num={
                max_num!r} max_chain_length={
                max_chain_length!r} max_chain_length_count={
                max_chain_length_count!r}")
    return max_chain_length_count


def main() -> int:
    print(solve(max_num=int(argv[1])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
