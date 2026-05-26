#! /usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""n of m secret sharing for fixed-size AES-256 keys.

Shamir's secret sharing over the prime field GF(2**521 - 1). The secret is a
32-byte (256-bit) AES-256 key, interpreted as the constant term of a random
polynomial of degree 'threshold - 1'. Each share picks a uniformly random
distinct non-zero x in the field and evaluates the polynomial there; any
'threshold' shares recover the secret via Lagrange interpolation at x = 0.

Share format::

    <hex_x><hex_y>

Both 'hex_x' and 'hex_y' are zero-padded to 131 lowercase hex characters
(ceil(521 / 4)), so each share string is always 262 characters and extraction
is 'x, y = s[:131], s[131:]'.
"""
from __future__ import annotations

from secrets import randbelow

#: 13th Mersenne prime; comfortably larger than a 256-bit secret.
_PRIME: int = 2 ** 521 - 1
#: Length of an AES-256 key in bytes.
_SECRET_BYTES: int = 32
#: Hex-character width sufficient to represent any value < _PRIME.
_HEX_WIDTH: int = 131


def _eval_poly(poly: list[int], x: int) -> int:
    """Evaluate 'poly' at 'x' (Horner's method) modulo '_PRIME'."""
    result: int = 0
    for coeff in reversed(poly):
        result = (result * x + coeff) % _PRIME
    return result


def _interpolate_at_zero(points: list[tuple[int, int]]) -> int:
    """Lagrange-interpolate the polynomial value at 'x = 0' from 'points' modulo '_PRIME'."""
    result: int = 0
    for i, (xi, yi) in enumerate(points):
        num: int = 1
        den: int = 1
        for j, (xj, _) in enumerate(points):
            if i == j:
                continue
            num = (num * -xj) % _PRIME
            den = (den * (xi - xj)) % _PRIME
        result = (result + yi * num * pow(den, -1, _PRIME)) % _PRIME
    return result


def split(secret: bytes, num_shares: int, threshold: int) -> list[str]:
    """
    Split a 32-byte AES-256 key into 'num_shares' shares; any 'threshold' of them reconstruct it.

    Args:
        secret: Exactly 32 bytes (256 bits).
        num_shares: Total number of shares to produce; must be >= threshold.
        threshold: Minimum shares needed to reconstruct; must satisfy 1 <= threshold <= num_shares.

    Returns:
        A list of 'num_shares' share strings, each of length 2 * 131 = 262 hex characters.

    Raises:
        ValueError: If the secret has the wrong size, or threshold/num_shares are out of range.
    """
    if len(secret) != _SECRET_BYTES:
        raise ValueError(f'secret must be exactly {_SECRET_BYTES} bytes, got {len(secret)}')
    if not 1 <= threshold <= num_shares:
        raise ValueError('require 1 <= threshold <= num_shares')

    poly: list[int] = [int.from_bytes(secret, 'big')] + [randbelow(_PRIME) for _ in range(threshold - 1)]

    xs: set[int] = set()
    while len(xs) < num_shares:
        xs.add(randbelow(_PRIME - 1) + 1)

    return [f'{x:0{_HEX_WIDTH}x}{_eval_poly(poly, x):0{_HEX_WIDTH}x}' for x in xs]


def reconstruct(shares: list[str]) -> bytes:
    """
    Reconstruct the 32-byte AES-256 key from a list of shares.

    Args:
        shares: At least 'threshold' distinct shares produced by 'split()' from the same secret.

    Returns:
        The original 32-byte key.

    Raises:
        ValueError: If the share list is empty, malformed, contains duplicate x coordinates,
            or yields a value too large to be a 256-bit key (wrong threshold or corruption).
    """
    if not shares:
        raise ValueError('need at least one share')

    points: list[tuple[int, int]] = []
    seen: set[int] = set()
    for s in shares:
        if len(s) != 2 * _HEX_WIDTH:
            raise ValueError(f'share must be {2 * _HEX_WIDTH} hex chars, got {len(s)}')
        x: int = int(s[:_HEX_WIDTH], 16)
        y: int = int(s[_HEX_WIDTH:], 16)
        if x in seen:
            raise ValueError(f'duplicate share index {x:x}')
        seen.add(x)
        points.append((x, y))

    secret_int: int = _interpolate_at_zero(points)
    if secret_int.bit_length() > _SECRET_BYTES * 8:
        raise ValueError('reconstructed value out of range; wrong threshold or corrupted shares')
    return secret_int.to_bytes(_SECRET_BYTES, 'big')


__all__ = ('split', 'reconstruct')
