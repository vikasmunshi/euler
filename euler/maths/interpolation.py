#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interpolation utilities

Numerical helpers for constructing and evaluating interpolation polynomials
commonly used in Project Euler style analyses. Provides Lagrange and Newton
form interpolants, a safe polynomial evaluator (Horner’s method), and a helper
that constructs a standard-form polynomial passing through given points.

Public API
- lagrange_interpolation(x_values, y_values, x): evaluate the Lagrange
  interpolation polynomial at x.
- newton_interpolation(x_values, y_values, x): evaluate the Newton divided-
  differences interpolation polynomial at x.
- eval_polynomial(polynomial, x): evaluate a standard-form polynomial using
  Horner’s rule.
- construct_polynomial(x_values, y_values): return standard-form coefficients
  for the unique polynomial through the points.

Examples
>>> from euler.maths.interpolation import lagrange_interpolation, newton_interpolation
>>> lagrange_interpolation(x_values=[1, 2, 3], y_values=[1, 4, 9], x=2.5)
6.25
>>> newton_interpolation(x_values=[0, 1, 2], y_values=[1, 3, 7], x=0.5)
1.75
"""
from math import isclose
from typing import List, Sequence, Tuple

# Define a variable for numeric types that can be used in interpolation
Numeric = int | float

# Type definition for polynomial representation as a tuple of coefficients
# where the index represents the power (e.g., [a₀, a₁, a₂] for a₀ + a₁x + a₂x²)
Polynomial = Tuple[Numeric, ...]


class InterpolationError(ValueError):
    """
    Error raised for invalid arguments or inconsistent input to interpolation helpers.

    Typical causes include mismatched x/y lengths or duplicate x-values that would
    lead to division by zero in basis construction or divided differences.
    """
    pass


def eval_polynomial(polynomial: Polynomial, x: Numeric) -> float:
    """
    Evaluate a polynomial at a given point using Horner’s method.

    The polynomial is given in standard form as coefficients (a0, a1, a2, ...)
    representing a0 + a1*x + a2*x^2 + ...

    Args:
        polynomial (Tuple[int | float, ...]): Coefficients in increasing powers of x.
        x (int | float): Point at which to evaluate the polynomial.

    Returns:
        float: The value of the polynomial at x.

    Examples:
        >>> eval_polynomial((1, 2, 1), 3)  # 1 + 2x + x² at x=3
        16.0
        >>> eval_polynomial((5, 0, -2), 2)  # 5 - 2x² at x=2
        -3.0
    """
    result = 0.0
    for coef in reversed(polynomial):
        result = result * x + coef
    return result


def lagrange_interpolation(*, x_values: Sequence[Numeric], y_values: Sequence[Numeric], x: Numeric) -> float:
    """
    Evaluate the Lagrange interpolation polynomial at x.

    Constructs the unique degree-(n-1) polynomial that passes through the
    provided (x_i, y_i) pairs using the Lagrange basis. If x exactly matches
    one of the x_i, the corresponding y_i is returned as a float.

    Args:
        x_values (Sequence[int | float]): X-coordinates of data points. Must be unique.
        y_values (Sequence[int | float]): Y-coordinates corresponding to x_values.
        x (int | float): Point at which to evaluate the interpolant.

    Returns:
        float: Interpolated y-value at x.

    Raises:
        InterpolationError: If x_values and y_values have different lengths, or
            if x_values contain duplicates.

    Notes:
        An early-break optimization skips work when a basis term becomes
        numerically zero (abs_tol=1e-10) to save time without affecting the
        final sum.

    Examples:
        >>> lagrange_interpolation(x_values=[1, 2, 3], y_values=[1, 4, 9], x=2.5)
        6.25
    """
    if (num_x_vals := len(x_values)) != len(y_values):
        raise InterpolationError('x_values and y_values must have the same length')
    if len(set(x_values)) != num_x_vals:
        raise InterpolationError('x_values must contain unique values to avoid division by zero')
    for i, xi in enumerate(x_values):
        if x == xi:
            return float(y_values[i])
    result = 0.0
    for i, yi in enumerate(y_values):
        basis = 1.0
        for j, xj in enumerate(x_values):
            if i != j:
                basis *= (x - xj) / (x_values[i] - xj)
                if isclose(basis, 0.0, abs_tol=1e-10):
                    break
        result += yi * basis
    return result


def newton_interpolation(*, x_values: Sequence[Numeric], y_values: Sequence[Numeric], x: Numeric) -> float:
    """
    Evaluate the Newton divided-differences interpolant at x.

    Computes divided differences from the provided data and evaluates the
    Newton-form polynomial via Horner’s rule.

    Args:
        x_values (Sequence[int | float]): X-coordinates of data points. Must be unique.
        y_values (Sequence[int | float]): Y-coordinates corresponding to x_values.
        x (int | float): Point at which to evaluate the interpolant.

    Returns:
        float: Interpolated y-value at x.

    Raises:
        InterpolationError: If x_values and y_values have different lengths, or
            if x_values contain duplicates.

    Examples:
        >>> newton_interpolation(x_values=[1, 2, 3], y_values=[1, 4, 9], x=2.5)
        6.25
    """
    if (num_x_vals := len(x_values)) != len(y_values):
        raise InterpolationError('x_values and y_values must have the same length')
    if len(set(x_values)) != num_x_vals:
        raise InterpolationError('x_values must contain unique values to avoid division by zero')
    coeffs: List[float] = list(map(float, y_values))
    for j in range(1, num_x_vals):
        for i in range(num_x_vals - 1, j - 1, -1):
            coeffs[i] = (coeffs[i] - coeffs[i - 1]) / (x_values[i] - x_values[i - j])
    result = coeffs[num_x_vals - 1]
    for i in range(num_x_vals - 2, -1, -1):
        result = result * (x - x_values[i]) + coeffs[i]
    return result


def construct_polynomial(*, x_values: Sequence[Numeric], y_values: Sequence[Numeric]) -> Polynomial:
    """
    Construct the standard-form polynomial that passes through given points.

    Builds Newton’s divided differences from the data, then converts the Newton
    form to standard coefficients (a0, a1, a2, ...). The result can be evaluated
    with eval_polynomial.

    Args:
        x_values (Sequence[int | float]): X-coordinates of data points. Must be unique.
        y_values (Sequence[int | float]): Y-coordinates corresponding to x_values.

    Returns:
        Tuple[int | float, ...]: Coefficients (a0, a1, a2, ...) representing
            a0 + a1*x + a2*x^2 + ...

    Raises:
        InterpolationError: If x_values and y_values have different lengths, or
            if x_values contain duplicates.

    Examples:
        >>> construct_polynomial(x_values=[1, 2, 3], y_values=[1, 4, 9])
        (0.0, 0.0, 1.0)
        >>> construct_polynomial(x_values=[0, 1, 2], y_values=[1, 3, 7])
        (1.0, 1.0, 1.0)

    Notes:
        Converts from Newton’s form to standard form so downstream consumers can
        evaluate with a simple Horner’s method.
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
