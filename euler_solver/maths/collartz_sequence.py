#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Collatz Sequence Utilities"""
from __future__ import annotations

cache = {1: 1}


def collatz_sequence_length(number: int) -> int:
    """Calculate the Collatz sequence length iteratively and efficiently."""
    intermediate_steps = []  # Track all steps in the sequence
    length = 0

    # Traverse the Collatz sequence
    while number != 1 and number not in cache:
        intermediate_steps.append(number)
        if number % 2 == 0:
            number //= 2
        else:
            number = 3 * number + 1
        length += 1

    # Add cached length to the computed length
    length += cache[number]  # This is safe because earlier computation must be correct

    # Update cache for all intermediate numbers
    for i, value in enumerate(intermediate_steps):
        # Only update cache if the number is not already present to maintain correctness
        if value not in cache:
            cache[value] = length - i

    return length
