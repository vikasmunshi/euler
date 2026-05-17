#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 84: Monopoly Odds [Level 7]. """
from __future__ import annotations

import collections
import itertools
import random
import typing
from sys import argv, stderr
from time import perf_counter
from typing import Any

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


class Movement(typing.Protocol):

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


def card_stack(cards: list[Movement]) -> typing.Generator[Movement, None, None]:
    random.shuffle(cards)
    for card in itertools.cycle(cards):
        yield card


def community_chest_cards() -> typing.Generator[Movement, None, None]:
    cards: list[Movement] = [ForwardMovement("GO"), ForwardMovement("JAIL")] + [NullMovement()] * 14
    yield from card_stack(cards)


class BackwardMovement(Movement):

    def seek(self, position: int) -> int:
        return (position - 3 + board_size) % board_size


def chance_cards() -> typing.Generator[Movement, None, None]:
    cards: list[Movement] = [
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
    first = random.randint(1, dice_size)
    second = random.randint(1, dice_size)
    return first + second


def simulate(*, dice_size: int, simulations: int) -> list[tuple[float, str, int]]:
    position: int = 0
    visited_fields: dict[str, int] = collections.defaultdict(int)
    chance_cards_iter: typing.Iterator[Movement] = chance_cards()
    community_chest_cards_iter: typing.Iterator[Movement] = community_chest_cards()
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


def main(**kwargs: Any) -> int:
    """
    Usage: ./file.py <kwarg>... [--runs=1] [--show]
    Output: "<runs> <avg_seconds> <result>"
    """
    try:
        runs_arg: str = next((arg for arg in argv[1:] if arg.startswith("--runs=")))
        runs: int = int(runs_arg.split("=", 1)[1])
        assert runs > 0
    except (AssertionError, StopIteration, ValueError):
        runs = 1
    elapsed: list[float] = []
    result: int | None = None
    rc: int = 0
    errors: list[str] = []
    for _ in range(runs):
        _start, _result, _stop = (perf_counter(), solve(**kwargs), perf_counter())
        elapsed.append(_stop - _start)
        if result is not None and _result != result:
            errors.append(f"Expected consistent result, got {_result} previous result={result}")
        result = _result
    if result is None:
        errors.append("Expected a result, got None")
    average: float = sum(elapsed) / len(elapsed)
    if errors:
        print("\n".join(errors), file=stderr)
        rc = 1
    print(f"{runs} {average} {result}")
    return rc


if __name__ == "__main__":
    raise SystemExit(main(dice_size=int(argv[1]), simulations=int(argv[2])))
