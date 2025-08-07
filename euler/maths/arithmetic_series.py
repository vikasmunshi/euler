#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Arithmetic Series"""
from __future__ import annotations

from typing import Generator, overload


def generate_arithmetic_series(d: int, *,
                               min_num: int | None = None,
                               max_num: int | float | None) -> Generator[int, None, None]:
    if max_num is None:
        max_num = float('inf')
    if min_num is None:
        n = 0
    elif min_num % d == 0:
        n = min_num
        yield n
    else:
        n = d * (min_num // d)
    while (n := n + d) <= max_num:
        yield n


@overload
def sum_arithmetic_series(*, first_term: int, common_difference: int, max_limit: int, ) -> int: ...


@overload
def sum_arithmetic_series(*, first_term: int, common_difference: int, number_of_terms: int, ) -> int: ...


def sum_arithmetic_series(**kwargs: int) -> int:
    if 'max_limit' in kwargs:
        first_term: int = kwargs['first_term']
        common_difference: int = kwargs['common_difference']
        max_limit: int = kwargs['max_limit']
        number_of_terms: int = (max_limit - first_term - 1) // common_difference
        return (first_term * number_of_terms) + (common_difference * number_of_terms * (number_of_terms + 1) // 2)
    elif 'number_of_terms' in kwargs:
        first_term = kwargs['first_term']
        common_difference = kwargs['common_difference']
        number_of_terms = kwargs['number_of_terms']
        return (first_term * number_of_terms) + (common_difference * number_of_terms * (number_of_terms + 1) // 2)
    else:
        raise ValueError('Either max_limit or number_of_terms must be provided')
