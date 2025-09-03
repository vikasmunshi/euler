#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Arithmetic series utilities

Helpers for generating and summing arithmetic progressions commonly used in
Project Euler problems. The module exposes a simple generator for multiples of a
given common difference within optional bounds and a closed-form summation
utility.

Public API
- generate_arithmetic_series(d, *, min_num=None, max_num): yield terms in the
  arithmetic progression with step d within the given bounds.
- sum_arithmetic_series(*, first_term, common_difference, max_limit | number_of_terms):
  compute the sum of terms using a closed form.

Notes
- generate_arithmetic_series treats bounds as follows:
  - min_num: if None, generation starts from d; if provided and already a multiple
    of d, the first yielded value is min_num; otherwise it starts from the first
    multiple of d greater than min_num. A min_num of 0 yields from d (0 is not emitted).
  - max_num: if None, the generator is infinite; otherwise it yields values ≤ max_num.
- sum_arithmetic_series requires exactly one of max_limit or number_of_terms.
  For max_limit, terms are strictly less than max_limit + 1 and start at first_term;
  if max_limit <= first_term there are no terms and the sum is 0.

Examples
>>> from euler_solver.maths.arithmetic_series import generate_arithmetic_series, sum_arithmetic_series
>>> list(generate_arithmetic_series(d=3, min_num=None, max_num=10))
[3, 6, 9]
>>> sum_arithmetic_series(first_term=2, common_difference=2, number_of_terms=5)
30
>>> sum_arithmetic_series(first_term=3, common_difference=3, max_limit=10)
18
"""
from __future__ import annotations

from typing import Generator, overload


def generate_arithmetic_series(d: int, *,
                               min_num: int | None = None,
                               max_num: int | None) -> Generator[int, None, None]:
    """
    Generate terms of an arithmetic progression with step d within bounds.

    The sequence starts at the first multiple of d that is ≥ min_num (or d when
    min_num is None or 0), and yields successive multiples spaced by d. If max_num
    is None, the generator is infinite; otherwise it yields values ≤ max_num.

    Args:
        d (int): Positive common difference of the progression.
        min_num (int | None): Lower bound (inclusive) for yielded values. If None,
            start from d. If provided and already a multiple of d, the first yield
            equals min_num; otherwise start from the next multiple above min_num.
        max_num (int | None): Upper bound (inclusive) for yielded values. If None,
            generate indefinitely.

    Yields:
        int: Next term of the progression.

    Raises:
        ValueError: If d <= 0, or if min_num/max_num are not None or non-negative ints.
    """
    if not isinstance(d, int) or d <= 0:
        raise ValueError('Common difference must be a natural number greater than zero.')

    if not (min_num is None or (isinstance(min_num, int) and min_num >= 0)):
        raise ValueError('min_num must be None or a natural number (greater than or equal to zero).')

    if not (max_num is None or (isinstance(max_num, int) and max_num >= 0)):
        raise ValueError('max_num must be None or a natural number (greater than or equal to zero).')

    # Calculate the last valid term
    stop: int | None = None if max_num is None else int(max_num // d) * d

    # Calculate the first valid term, excluding zero
    start: int = d if min_num is None or min_num == 0 else ((min_num + d - 1) // d) * d

    # If the start term exceeds max_num, no terms exist
    if stop is not None and start > stop:
        return

    # Handle bounded or unbounded max_num
    if stop is None:
        # Generate terms indefinitely, as max_num is unbounded
        term = start
        while True:
            yield term
            term += d
    else:
        # Generate terms using a step
        for term in range(start, stop + 1, d):
            yield term


@overload
def sum_arithmetic_series(*, first_term: int, common_difference: int, max_limit: int, ) -> int: ...


@overload
def sum_arithmetic_series(*, first_term: int, common_difference: int, number_of_terms: int, ) -> int: ...


def sum_arithmetic_series(*, first_term: int, common_difference: int,
                          max_limit: int | None = None, number_of_terms: int | None = None) -> int:
    """
    Compute the sum of an arithmetic progression using a closed form.

    Provide exactly one of max_limit or number_of_terms:
    - If max_limit is given, the number of terms n is determined by how many terms
      starting at first_term with step common_difference are ≤ max_limit. When
      max_limit <= first_term there are no terms and the sum is 0.
    - If number_of_terms is given, n equals that value (may be 0).

    Args:
        first_term (int): The first term (a) of the progression.
        common_difference (int): The common difference (d).
        max_limit (int | None): Optional upper bound (inclusive) for the terms.
        number_of_terms (int | None): Optional explicit number of terms n.

    Returns:
        int: The sum S_n computed with S_n = n/2 * (2a + (n-1)d).

    Raises:
        ValueError: If neither or both of max_limit and number_of_terms are provided.
    """
    if max_limit is not None:
        # Compute the number of terms that fit within the limitation of max_limit
        if max_limit <= first_term:
            return 0  # No terms in the series if max_limit is too small
        n = (max_limit - first_term - 1) // common_difference + 1
    elif number_of_terms is not None:
        n = number_of_terms
    else:
        raise ValueError("You must provide either `max_limit` or `number_of_terms`.")

    # Calculate the sum of the series using the sum formula: S_n = n/2 * (2a + (n-1)d)
    return n * (2 * first_term + (n - 1) * common_difference) // 2
