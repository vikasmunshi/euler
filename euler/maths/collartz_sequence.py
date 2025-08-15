#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Collatz Sequence Utilities"""
from __future__ import annotations

from functools import lru_cache


@lru_cache(maxsize=None)
def collatz_sequence_length(number: int) -> int:
    """Calculate the Collatz sequence length using memoization."""
    if number == 1:
        return 1
    if number % 2 == 0:
        return 1 + collatz_sequence_length(number // 2)
    else:
        return 1 + collatz_sequence_length(3 * number + 1)
