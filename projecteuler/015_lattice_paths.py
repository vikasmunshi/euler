#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-
"""
https://projecteuler.net/problem=15
Starting in the top left corner of a 2×2 grid, and only being able to move to the right and down,
there are exactly 6 routes to the bottom right corner.


How many such routes are there through a 20×20 grid?
Answer: 137846528820
"""
from math import factorial


def lattice_paths(lattice_size: int) -> int:
    return factorial(2 * lattice_size) // (factorial(lattice_size) ** 2)


if __name__ == '__main__':
    from .evaluate import Watchdog

    with Watchdog() as wd:
        result = wd.evaluate_range(lattice_paths, answers={2: 6, 20: 137846528820})
