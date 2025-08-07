#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
  Project Euler Problem 15: Lattice Paths.

  Problem Statement:
    Starting in the top left corner of a 2 x 2 grid, and only being able to move
    to the right and down, there are exactly 6 routes to the bottom right
    corner.

    How many such routes are there through a 20 x 20 grid?

  Solution Approach:
    This problem can be approached using combinatorics, specifically the concept
    of lattice paths. Each path consists of moves to the right and moves downward.
    To find the total number of routes in a 20 x 20 grid, one needs to determine
    the number of unique sequences of these moves.

    Since each path has exactly 20 moves to the right and 20 moves down, the
    problem reduces to choosing the positions of either the right moves or the down
    moves in a sequence of 40 steps. This can be computed using binomial
    coefficients.

    An efficient method involves calculating the binomial coefficient "40 choose
    20". Implementing this calculation in a program using an iterative or
    recursive approach with memoization can handle large values accurately.

    Alternatively, understanding Pascal's triangle or dynamic programming can
    provide other methods to solve this problem programmatically.

  Test Cases:
    preliminary:
      lattice_size=2,
      answer=6.

    main:
      lattice_size=20,
      answer=137846528820.

    extended:
      lattice_size=200,
      answer=1029525001354144329729758803204019867572109253810776482348490595759
             23332372651958598336595518976492951564048597506774120.


  Answer: 137846528820
  URL: https://projecteuler.net/problem=15
"""
from __future__ import annotations

from math import factorial

from euler.logger import logger
from euler.setup import TestCaseCategory, evaluate, register_solution


@register_solution(euler_problem=15, test_case_category=TestCaseCategory.EXTENDED)
def lattice_paths(*, lattice_size: int) -> int:
    return factorial(2 * lattice_size) // factorial(lattice_size) ** 2


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=15, time_out_in_seconds=300, mode='evaluate'))
