#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Interpolation utility module for numerical analysis.

This module provides different interpolation methods for approximating values between data points.
Current implementations include Lagrange and Newton polynomial interpolation methods.

Interpolation is a mathematical technique to estimate unknown values that fall between known data points.
This is particularly useful in numerical analysis, data visualization, and scientific computing where
we need to construct new data points within the range of a discrete set of known data points.

Available Functions:
    - lagrange_interpolation: Computes interpolation using Lagrange basis polynomials
    - newton_interpolation: Computes interpolation using Newton's divided differences method
    - eval_polynomial: Evaluates a polynomial at a given point

Typical Usage:
    >>> from euler.maths.interpolation import lagrange_interpolation
    >>> lagrange_interpolation(x_values=[1, 2, 3], y_values=[1, 4, 9], x=2.5)
    6.25  # Interpolated value at x=2.5 for the points (1,1), (2,4), (3,9)

    >>> from euler.maths.interpolation import newton_interpolation
    >>> newton_interpolation(x_values=[0, 1, 2], y_values=[1, 3, 7], x=0.5)
    1.75  # Interpolated value at x=0.5 using Newton's method
"""
from math import isclose
from typing import List, Sequence, Tuple

from euler.types import EulerError

# Define a variable for numeric types that can be used in interpolation
Numeric = int | float

# Type definition for polynomial representation as a tuple of coefficients
# where the index represents the power (e.g., [a₀, a₁, a₂] for a₀ + a₁x + a₂x²)
Polynomial = Tuple[Numeric, ...]


class InterpolationError(EulerError):
    """Exception raised for errors in interpolation methods."""
    pass


def eval_polynomial(polynomial: Polynomial, x: Numeric) -> float:
    """Evaluate a polynomial at a given point x.

    The polynomial is represented as a tuple of coefficients where the index corresponds to the power.
    For example, the polynomial a₀ + a₁x + a₂x² is represented as (a₀, a₁, a₂).

    Args:
        polynomial: A tuple of coefficients where the index represents the power of x
        x: The point at which to evaluate the polynomial

    Returns:
        The value of the polynomial at the given point

    Examples:
        >>> eval_polynomial((1, 2, 1), 3)  # Evaluates 1 + 2x + x² at x=3
        16.0  # 1 + 2*3 + 3² = 1 + 6 + 9 = 16

        >>> eval_polynomial((5, 0, -2), 2)  # Evaluates 5 - 2x² at x=2
        -3.0  # 5 - 2*2² = 5 - 2*4 = 5 - 8 = -3
    """
    # Use Horner's method for efficient polynomial evaluation
    result = 0.0
    for coef in reversed(polynomial):
        result = result * x + coef
    return result


def lagrange_interpolation(*, x_values: Sequence[Numeric], y_values: Sequence[Numeric], x: Numeric) -> float:
    """
    Compute the Lagrange polynomial interpolation for a given set of points and a target x value.

    The Lagrange interpolation method constructs a polynomial of degree (n-1) that passes through
    n points. This implementation uses the Lagrange basis form of the interpolation polynomial.

    Args:
        x_values: Sequence of x-coordinates of the points to interpolate (must be unique)
        y_values: Sequence of y-coordinates of the points to interpolate
        x: The x-coordinate at which to evaluate the interpolation polynomial

    Returns:
        The interpolated y-value at the given x-coordinate

    Examples:
        >>> lagrange_interpolation(x_values=[1, 2, 3], y_values=[1, 4, 9], x=2.5)
        6.25  # Interpolated value at x=2.5 for the points (1,1), (2,4), (3,9)
    """
    # Validate input parameters
    if (num_x_vals := len(x_values)) != len(y_values):
        raise InterpolationError('x_values and y_values must have the same length')

    # Check for duplicate x values which would cause division by zero
    if len(set(x_values)) != num_x_vals:
        raise InterpolationError('x_values must contain unique values to avoid division by zero')

    # If x exactly matches one of the input points, return the corresponding y value
    for i, xi in enumerate(x_values):
        if x == xi:  # Exact match found
            return float(y_values[i])

    # No exact match found, compute interpolation
    result = 0.0
    for i, yi in enumerate(y_values):
        # Compute Lagrange basis polynomial for this point
        basis = 1.0
        for j, xj in enumerate(x_values):
            if i != j:
                # Use factored form to avoid potential overflow
                basis *= (x - xj) / (x_values[i] - xj)
                # Break early if basis becomes zero (optimization)
                if isclose(basis, 0.0, abs_tol=1e-10):
                    break
        result += yi * basis
    return result


def newton_interpolation(*, x_values: Sequence[Numeric], y_values: Sequence[Numeric], x: Numeric) -> float:
    """
    Compute the Newton polynomial interpolation for a given set of points and a target x value.

    Newton's interpolation method constructs a polynomial using divided differences,
    which can be more numerically stable and efficient than Lagrange's method,
    especially when adding new points to an existing interpolation.

    Args:
        x_values: Sequence of x-coordinates of the points to interpolate (must be unique)
        y_values: Sequence of y-coordinates of the points to interpolate
        x: The x-coordinate at which to evaluate the interpolation polynomial

    Returns:
        The interpolated y-value at the given x-coordinate

    Examples:
        >>> newton_interpolation(x_values=[1, 2, 3], y_values=[1, 4, 9], x=2.5)
        6.25  # Interpolated value at x=2.5 for the points (1,1), (2,4), (3,9)
    """
    # Validate input parameters
    if (num_x_vals := len(x_values)) != len(y_values):
        raise InterpolationError('x_values and y_values must have the same length')

    # Check for duplicate x values which would cause division by zero
    if len(set(x_values)) != num_x_vals:
        raise InterpolationError('x_values must contain unique values to avoid division by zero')

    # Create a copy of y_values to store divided differences
    coeffs: List[float] = list(map(float, y_values))

    # Calculate the divided differences (coefficients for Newton's polynomial)
    for j in range(1, num_x_vals):
        for i in range(num_x_vals - 1, j - 1, -1):
            coeffs[i] = (coeffs[i] - coeffs[i - 1]) / (x_values[i] - x_values[i - j])

    # Evaluate the polynomial using Horner's rule
    result = coeffs[num_x_vals - 1]
    for i in range(num_x_vals - 2, -1, -1):
        result = result * (x - x_values[i]) + coeffs[i]

    return result


def construct_polynomial(*, x_values: Sequence[Numeric], y_values: Sequence[Numeric]) -> Polynomial:
    """Construct a polynomial that passes through the given points.

    This function uses Newton's divided differences method to construct a polynomial
    that interpolates the given data points. The returned polynomial can be evaluated
    using the eval_polynomial function.

    Args:
        x_values: Sequence of x-coordinates of the points to interpolate (must be unique)
        y_values: Sequence of y-coordinates of the points to interpolate

    Returns:
        A polynomial as a tuple of coefficients in the standard form (a₀, a₁, a₂, ...)
        where the index represents the power of x

    Examples:
        >>> construct_polynomial(x_values=[1, 2, 3], y_values=[1, 4, 9])
        (0.0, 0.0, 1.0)  # Represents f(x) = x²

        >>> construct_polynomial(x_values=[0, 1, 2], y_values=[1, 3, 7])
        (1.0, 1.0, 1.0)  # Represents f(x) = 1 + x + x²

    Notes:
        This implementation converts from Newton's form to the standard form of a polynomial.
        The returned polynomial can be evaluated with eval_polynomial.
    """
    # Validate input parameters
    if (num_x_vals := len(x_values)) != len(y_values):
        raise InterpolationError('x_values and y_values must have the same length')

    # Check for duplicate x values which would cause division by zero
    if len(set(x_values)) != num_x_vals:
        raise InterpolationError('x_values must contain unique values to avoid division by zero')

    # Calculate divided differences (Newton's coefficients)
    newton_coeffs = list(map(float, y_values))
    for j in range(1, num_x_vals):
        for i in range(num_x_vals - 1, j - 1, -1):
            newton_coeffs[i] = (newton_coeffs[i] - newton_coeffs[i - 1]) / (x_values[i] - x_values[i - j])

    # Convert from Newton's form to standard form
    # Initialize polynomial with all zeros
    poly = [0.0] * num_x_vals

    # Iteratively convert Newton form to standard form
    for i in range(num_x_vals):
        # Add contribution of the current Newton coefficient
        # First, calculate the expanded term
        term = [0.0] * num_x_vals
        term[0] = 1.0  # Start with 1 (constant term)

        # Build the product (x-x₀)(x-x₁)...(x-xₖ₋₁) for k from 0 to i-1
        for k in range(i):
            # Multiply by (x-xₖ) using distributive property
            new_term = [0.0] * num_x_vals
            for j in range(min(i, num_x_vals - 1), -1, -1):
                if j < num_x_vals - 1:  # Multiply by x (shift right)
                    new_term[j + 1] += term[j]
                # Multiply by -xₖ
                new_term[j] -= x_values[k] * term[j]
            term = new_term

        # Add this term multiplied by the coefficient
        for j in range(num_x_vals):
            poly[j] += newton_coeffs[i] * term[j]

    return tuple(poly)
