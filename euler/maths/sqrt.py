#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Square Root Calculation Module

This module provides high-precision square root calculation methods suitable for
mathematical problems that require arbitrary precision. The implementations are
designed to work with integers and avoid floating-point imprecision issues.

Key features:
- High-precision square root calculations using various algorithms
- Integer-based calculations to avoid floating-point errors
- Methods that return string representations to preserve digit precision

Implemented algorithms:
- Heron's method (Newton's method): Fast convergence for most inputs
- Binary search method: Alternative approach with predictable performance

Typical usage:
    from euler.utils.sqrt import sqrt_heron_method

    # Calculate square root of 2 with 100 digits of precision
    sqrt_2 = sqrt_heron_method(2, 100)
"""


class SquareRootError(ValueError):
    """Exception raised for errors in square root calculations.

    This exception is raised when invalid inputs are provided to the square root
    calculation functions, such as negative numbers or other values that would
    result in undefined or invalid outputs.
    """
    pass


def sqrt_heron_method(number: int, digits: int) -> str:
    """Calculate square root with high precision using Heron's method.

    This function implements Heron's method (also known as Newton's method)
    to calculate square roots to a specified number of digits. It uses an
    iterative approach that converges to the square root.

    Args:
        number: The number to calculate the square root of
        digits: The number of digits of precision required

    Returns:
        A string representation of the square root with the specified number of digits

    Note:
        The algorithm multiplies the input by 10^(2*digits) to achieve the desired
        precision in the integer domain, then returns the result as a string with
        the specified number of digits.

    Example:
        >>> sqrt_heron_method(2, 10)
        '1414213562'
        >>> sqrt_heron_method(3, 5)
        '17320'
        >>> sqrt_heron_method(0, 5)
        '0'
    """
    # Handle special case of zero
    if number == 0:
        return '0' * min(1, digits)

    # Validate input
    if number < 0:
        raise SquareRootError(f'Cannot calculate square root of negative number: {number}')

    number *= 10 ** (2 * digits)
    sqrt = number
    while sqrt != (sqrt := (sqrt + number // sqrt) // 2):
        pass
    return str(sqrt)[:digits]


def sqrt_binary_search(number: int, digits: int) -> str:
    """Calculate square root with high precision using binary search.

    This function implements a binary search approach to calculate square roots
    to a specified number of digits. While typically slower than Heron's method,
    it provides predictable performance characteristics regardless of input.

    Args:
        number: The number to calculate the square root of
        digits: The number of digits of precision required

    Returns:
        A string representation of the square root with the specified number of digits

    Raises:
        SquareRootError: If number is negative

    Note:
        This implementation is useful as an alternative when Heron's method
        encounters convergence issues for certain inputs.

    Example:
        >>> sqrt_binary_search(2, 10)
        '1414213562'
        >>> sqrt_binary_search(0, 5)
        '0'
    """
    # Handle special case of zero
    if number == 0:
        return '0' * min(1, digits)

    # Validate input
    if number < 0:
        raise SquareRootError(f'Cannot calculate square root of negative number: {number}')

    # Scale the number to get desired precision
    scaled_number = number * (10 ** (2 * digits))

    # Set binary search boundaries
    low = 0
    high = scaled_number

    # Binary search loop
    while high - low > 1:
        mid = (low + high) // 2
        if mid * mid <= scaled_number:
            low = mid
        else:
            high = mid

    # Return the result with correct number of digits
    return str(low)[:digits]
