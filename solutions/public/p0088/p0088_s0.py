#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 88: Product-sum Numbers [Level 8]. """
from __future__ import annotations

from solver.runners import runner


@runner.main
def solve(*args: str) -> str:
    """Recursive factorization search: each factorization (product P, sum S) of m factors >= 2
    yields a product-sum set of size k = m + (P - S) after padding with P - S ones. The bound
    N <= 2k seeds the table and prunes branches; runtime is near-linear in max_k."""
    max_k = runner.parse_int(args[0])
    min_k = runner.parse_int(args[1])

    max_k += 1
    min_prod: list[int] = [2 * max_k] * max_k

    def find_product_sum(prod: int, total: int, count: int, start: int) -> None:
        """Relax min_prod for the set size implied by this factorization, then extend it."""
        k = prod - total + count
        if k < max_k:
            min_prod[k] = min(min_prod[k], prod)
            for i in range(start, max_k // prod * 2 + 1):
                find_product_sum(prod * i, total + i, count + 1, i)

    find_product_sum(1, 1, 1, min_k)
    if runner.show:
        print(min_prod[2:])
    return str(sum(set(min_prod[2:])))


if __name__ == "__main__":
    raise SystemExit(solve())
