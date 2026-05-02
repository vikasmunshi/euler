#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Migrated from:
  file: euler_solver/solutions/solutions_0001_0100/solution_0084/p0084.py
  func: solve_monopoly_odds_p0084_s0
"""

from __future__ import annotations

from collections import defaultdict
from itertools import cycle
from random import randint, shuffle
from sys import argv
from typing import Dict, Generator, Iterator, List, Protocol

board: tuple[str, ...] = (
    "GO",
    "A1",
    "CC1",
    "A2",
    "T1",
    "R1",
    "B1",
    "CH1",
    "B2",
    "B3",
    "JAIL",
    "C1",
    "U1",
    "C2",
    "C3",
    "R2",
    "D1",
    "CC2",
    "D2",
    "D3",
    "FP",
    "E1",
    "CH2",
    "E2",
    "E3",
    "R3",
    "F1",
    "F2",
    "U2",
    "F3",
    "G2J",
    "G1",
    "G2",
    "CC3",
    "G3",
    "R4",
    "CH3",
    "H1",
    "T2",
    "H2",
)


board_size: int = len(board)


class Movement(Protocol):

    def seek(self, position: int) -> int: ...


class ForwardMovement(Movement):

    def __init__(self, prefix: str) -> None:
        self._prefix = prefix

    def seek(self, position: int) -> int:
        while not board[position].startswith(self._prefix):
            position += 1
            position %= board_size
        return position


class NullMovement(Movement):

    def seek(self, position: int) -> int:
        return position


def card_stack(cards: list[Movement]) -> Generator[Movement, None, None]:
    shuffle(cards)
    for card in cycle(cards):
        yield card


def community_chest_cards() -> Generator[Movement, None, None]:
    cards: List[Movement] = [ForwardMovement("GO"), ForwardMovement("JAIL")] + [NullMovement()] * 14
    yield from card_stack(cards)


class BackwardMovement(Movement):

    def seek(self, position: int) -> int:
        return (position - 3 + board_size) % board_size


def chance_cards() -> Generator[Movement, None, None]:
    cards: List[Movement] = [
        ForwardMovement("GO"),
        ForwardMovement("JAIL"),
        ForwardMovement("C1"),
        ForwardMovement("E3"),
        ForwardMovement("H2"),
        ForwardMovement("R1"),
        ForwardMovement("R"),
        ForwardMovement("R"),
        ForwardMovement("U"),
        BackwardMovement(),
    ] + [NullMovement()] * 6
    yield from card_stack(cards)


def dice_roll(dice_size: int) -> int:
    first = randint(1, dice_size)
    second = randint(1, dice_size)
    return first + second


def simulate(*, dice_size: int, simulations: int) -> list[tuple[float, str, int]]:
    position: int = 0
    visited_fields: Dict[str, int] = defaultdict(int)
    chance_cards_iter: Iterator[Movement] = chance_cards()
    community_chest_cards_iter: Iterator[Movement] = community_chest_cards()
    for i in range(simulations):
        position += dice_roll(dice_size)
        position %= board_size
        if board[position].startswith("CC"):
            movement = next(community_chest_cards_iter)
            position = movement.seek(position)
        elif board[position].startswith("CH"):
            movement = next(chance_cards_iter)
            position = movement.seek(position)
        elif board[position] == "G2J":
            position = board.index("JAIL")
        visited_fields[board[position]] += 1
    results = sorted(
        [(100 * count / simulations, field, board.index(field)) for field, count in visited_fields.items()],
        reverse=True,
    )
    return results


def solve(*, dice_size: int, simulations: int) -> str:
    results = simulate(dice_size=dice_size, simulations=simulations)
    return "".join((f"{index:02d}" for percentage, field, index in results[:3]))


def main() -> int:
    print(solve(dice_size=int(argv[1]), simulations=int(argv[2])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
