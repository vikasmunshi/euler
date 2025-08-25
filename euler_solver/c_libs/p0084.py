#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Python wrapper for C implementations used in Project Euler problem 84 (Monopoly Odds).

Exposes:
- simulate(dice_size: int, simulations: int) -> list[tuple[float, str, int]]
  Runs the simulation in C and returns sorted results as (percentage, field_name, index).
"""
from __future__ import annotations

import ctypes

from euler_solver.c_libs import import_c_lib

__all__ = ['simulate', ]

# Load the C library built from src/p0084.c -> libs/lib_p0084.so
_c_lib = import_c_lib('lib_p0084')

# Bind C function: int monopoly_simulate(int dice_size, int simulations, long long* counts_out)
_c_func = getattr(_c_lib, 'monopoly_simulate')
_c_func.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_longlong)]
_c_func.restype = ctypes.c_int

# Board definition mirrors solution_0084/solution.py
_board: tuple[str, ...] = (
    'GO', 'A1', 'CC1', 'A2', 'T1', 'R1', 'B1', 'CH1', 'B2', 'B3', 'JAIL', 'C1', 'U1', 'C2', 'C3',
    'R2', 'D1', 'CC2', 'D2', 'D3', 'FP', 'E1', 'CH2', 'E2', 'E3', 'R3', 'F1', 'F2', 'U2', 'F3',
    'G2J', 'G1', 'G2', 'CC3', 'G3', 'R4', 'CH3', 'H1', 'T2', 'H2'
)


def simulate(*, dice_size: int, simulations: int) -> list[tuple[float, str, int]]:
    if not isinstance(dice_size, int) or dice_size <= 0:
        raise ValueError('dice_size must be a positive integer')
    if not isinstance(simulations, int) or simulations < 0:
        raise ValueError('simulations must be a non-negative integer')

    counts_arr: ctypes.Array[ctypes.c_longlong] = (ctypes.c_longlong * len(_board))()
    rc = int(_c_func(int(dice_size), int(simulations), counts_arr))
    if rc != 0:
        raise RuntimeError(f'C simulation failed with error code {rc}')

    total = float(simulations) if simulations > 0 else 1.0
    results = []
    count: ctypes.c_longlong
    for idx, count in enumerate(counts_arr):
        if count:
            percentage = 100.0 * float(count) / total
            results.append((percentage, _board[idx], idx))
    # Sort descending by percentage, then by index as tiebreaker to be stable
    results.sort(key=lambda t: (-t[0], t[2]))
    return results
