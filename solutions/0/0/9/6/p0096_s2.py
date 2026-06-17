#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 96: Su Doku [Level 4]. """
from __future__ import annotations

import typing

from solver.runners import runner

Grid = list[list[int]]
# Each cell's candidate digits are held as a 9-bit mask: bit (d-1) set => digit d is possible.
Values = list[int]
Units = list[tuple[tuple[int, ...], tuple[int, ...], tuple[int, ...]]]
Peers = list[tuple[int, ...]]
ALL_DIGITS = 0x1FF  # bits 0..8 set - every digit possible


def get_grids(file_url: str) -> typing.Generator[Grid, None, None]:
    """Yield each 9x9 puzzle from the resource file, skipping the 'Grid NN' labels."""
    grid: Grid = []
    for line in runner.get_text_file(file_url).splitlines(keepends=False):
        if line.startswith('Grid'):
            grid = []
        else:
            grid.append([int(d) for d in line.strip()])
        if len(grid) == 9:
            yield grid


def build_units_peers() -> tuple[Units, Peers]:
    """Precompute, for every cell, its three units (row/column/box) and its 20 peers."""
    units: Units = []
    peers: Peers = []
    for cell in range(81):
        row, col = cell // 9, cell % 9
        row_unit = tuple(row * 9 + k for k in range(9))
        col_unit = tuple(k * 9 + col for k in range(9))
        box_row, box_col = (row // 3) * 3, (col // 3) * 3
        box_unit = tuple((box_row + i) * 9 + (box_col + j) for i in range(3) for j in range(3))
        units.append((row_unit, col_unit, box_unit))
        peer_set: set[int] = set(row_unit) | set(col_unit) | set(box_unit)
        peer_set.discard(cell)
        peers.append(tuple(sorted(peer_set)))
    return units, peers


def eliminate(values: Values, cell: int, digit: int, units: Units, peers: Peers) -> bool:
    """Remove digit from a cell, then propagate naked/hidden singles; False on contradiction."""
    bit = 1 << (digit - 1)
    if not (values[cell] & bit):
        return True  # already eliminated
    values[cell] &= ~bit
    remaining = values[cell]
    if remaining == 0:
        return False  # nothing left - contradiction
    if remaining.bit_count() == 1:
        # Naked single: cell forced to one digit => strip that digit from all its peers.
        only = remaining.bit_length()
        for peer in peers[cell]:
            if not eliminate(values, peer, only, units, peers):
                return False
    for unit in units[cell]:
        # Hidden single: if digit can now go in only one place in this unit, place it there.
        places = [c for c in unit if values[c] & bit]
        if len(places) == 0:
            return False
        if len(places) == 1:
            if not assign(values, places[0], digit, units, peers):
                return False
    return True


def assign(values: Values, cell: int, digit: int, units: Units, peers: Peers) -> bool:
    """Fix a cell to digit by eliminating every other candidate (which propagates)."""
    others = values[cell] & ~(1 << (digit - 1))
    for d in range(1, 10):
        if others & (1 << (d - 1)):
            if not eliminate(values, cell, d, units, peers):
                return False
    return True


def search(values: Values, units: Units, peers: Peers) -> Values | None:
    """Depth-first guess on the unsolved cell with fewest candidates; propagate each guess."""
    cell = -1
    best = 10
    for c in range(81):
        count = values[c].bit_count()
        if count > 1 and count < best:
            best, cell = count, c
    if cell == -1:
        return values  # every cell down to one candidate - solved
    mask = values[cell]
    for d in range(1, 10):
        if mask & (1 << (d - 1)):
            trial = values[:]
            if assign(trial, cell, d, units, peers):
                result = search(trial, units, peers)
                if result is not None:
                    return result
    return None


def solve_one_grid(grid: Grid, units: Units, peers: Peers) -> int:
    """Seed the clues, propagate to a fixpoint, search if needed; return top-left number."""
    values: Values = [ALL_DIGITS] * 81
    for i in range(81):
        clue = grid[i // 9][i % 9]
        if clue and not assign(values, i, clue, units, peers):
            raise AssertionError('clue led to an immediate contradiction')
    solved = search(values, units, peers)
    assert solved is not None, 'failed to solve grid'
    return solved[0].bit_length() * 100 + solved[1].bit_length() * 10 + solved[2].bit_length()


@runner.main
def solve(*args: str) -> str:
    """Constraint propagation to a fixpoint plus depth-first search (after Norvig); sum the
    top-left 3-digit numbers. Worst case exponential, near-linear on these puzzles."""
    file_url = args[0]

    units, peers = build_units_peers()
    return str(sum(solve_one_grid(grid, units, peers) for grid in get_grids(file_url=file_url)))


if __name__ == "__main__":
    raise SystemExit(solve())
