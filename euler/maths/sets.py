#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Working with sets for Project Euler """
from __future__ import annotations

from itertools import combinations
from typing import Generator, Sequence


def gen_sub_sets[T](set_a: Sequence[T]) -> Generator[list[T], None, None]:
    n: int = len(set_a)
    for i in range(1 << n):
        subset: list[T] = []
        for j in range(n):
            if i & (1 << j):
                subset.append(set_a[j])
        yield subset


def are_disjoint[T](set_a: Sequence[T], set_b: Sequence[T]) -> bool:
    return set(set_a).isdisjoint(set_b)


def next_near_optimum_set(optimum_set_a: Sequence[int]) -> list[int]:
    b: int = optimum_set_a[len(optimum_set_a) // 2] if optimum_set_a else 1
    set_b = [b] + [i + b for i in optimum_set_a]
    return set_b


def is_special_sum_set(set_a: Sequence[int]) -> bool:
    if not set_a:
        return False
    n = len(set_a)
    if n == 1:
        return True

    # Step 1: Check the second rule directly for sorted set
    # If B has more elements than C, S(B) > S(C)
    set_a = sorted(set_a)
    for k in range(1, n // 2 + 1):
        if sum(set_a[:k + 1]) <= sum(set_a[-k:]):
            return False

    # Step 2: Ensure subset sums are unique
    subset_sums = set()
    for size in range(1, n + 1):
        for subset in combinations(set_a, size):
            subset_sum = sum(subset)
            if subset_sum in subset_sums:
                return False
            subset_sums.add(subset_sum)

    return True


def gen_close_by_ordered_sets(ordered_set_a: Sequence[int], variation: int = 2) -> Generator[list[int], None, None]:
    if not ordered_set_a:
        return
    n = len(ordered_set_a)
    if n == 1:
        yield [ordered_set_a[0]]
        return

    def gen_recursive(pos: int, current: list[int]) -> Generator[list[int], None, None]:
        if pos == n:
            yield current
            return
        if pos == 0:
            yield from gen_recursive(pos + 1, current + [ordered_set_a[0]])
        else:
            for val in range(max(1, ordered_set_a[pos] - variation), ordered_set_a[pos] + variation + 1):
                if current[pos - 1] < val:
                    yield from gen_recursive(pos + 1, current + [val])

    yield from gen_recursive(0, [])
