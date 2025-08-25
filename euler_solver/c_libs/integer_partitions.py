#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Python wrapper for C implementations for integer partitions (Problems 76, 77, 78). """
from __future__ import annotations

from euler_solver.c_libs import import_c_lib

__all__ = [
    'num_partitions_recursive',
    'num_partitions_simple_recursion',
    'num_prime_partitions_simple_recursion',
    'get_partitions_simple_recursion',
    'get_prime_partitions_simple_recursion'
]

# Load the C library built from src/integer_partitions.c -> libs/lib_integer_partitions.so
_c_lib = import_c_lib('lib_integer_partitions')

# Bindings
_num_partitions_recursive_c = _c_lib.num_partitions_recursive

_num_partitions_simple_recursion_c = _c_lib.num_partitions_simple_recursion

_num_prime_partitions_simple_recursion_c = _c_lib.num_prime_partitions_simple_recursion

_get_partitions_simple_recursion_c = _c_lib.get_partitions_simple_recursion

_get_prime_partitions_simple_recursion_c = _c_lib.get_prime_partitions_simple_recursion


def num_partitions_recursive(number: int) -> int:
    pass


def num_partitions_simple_recursion(*, number: int, slots: int) -> int:
    pass


def num_prime_partitions_simple_recursion(*, number: int, slots: int) -> int:
    pass


def get_partitions_simple_recursion(*, number: int, slots: int, safe_limit: int | None = None) -> list[list[int]]:
    pass


def get_prime_partitions_simple_recursion(*, number: int, slots: int, safe_limit: int | None = None) -> list[list[int]]:
    pass
