#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 84: Monopoly Odds [Level 8]. """
from __future__ import annotations

from solver.runners import runner

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
JAIL: int = board.index("JAIL")


def seek(start: int, prefix: str) -> int:
    """Advance clockwise from ``start`` to the next square whose name begins with ``prefix``."""
    position = start
    while not board[position].startswith(prefix):
        position = (position + 1) % board_size
    return position


def resolve(landing: int) -> dict[int, float]:
    """Distribution over *finishing* squares after stopping on ``landing``.

    Applies the board's square rules: G2J sends the player to jail; CC and CH draw a card
    (a uniform 1/16 each, the rest leaving the player in place). The Chance "go back 3" can
    land on CC3, so its destination is resolved recursively to chain into a Community Chest draw.
    """
    name = board[landing]
    if name == "G2J":
        return {JAIL: 1.0}
    if name.startswith("CC"):
        # 2/16 movement cards (Advance to GO, Go to Jail); 14/16 stay.
        return {0: 1 / 16, JAIL: 1 / 16, landing: 14 / 16}
    if name.startswith("CH"):
        # 10/16 movement cards; 6/16 stay. "next R" appears twice (2/16 combined).
        targets = [
            0,                          # Advance to GO
            JAIL,                       # Go to Jail
            board.index("C1"),          # Go to C1
            board.index("E3"),          # Go to E3
            board.index("H2"),          # Go to H2
            board.index("R1"),          # Go to R1
            seek(landing + 1, "R"),     # next Railway
            seek(landing + 1, "R"),     # next Railway (again)
            seek(landing + 1, "U"),     # next Utility
        ]
        distribution: dict[int, float] = {}
        for target in targets:
            distribution[target] = distribution.get(target, 0.0) + 1 / 16
        # "Go back 3 squares" may land on CC3, which then triggers a Community Chest draw.
        for square, probability in resolve((landing - 3) % board_size).items():
            distribution[square] = distribution.get(square, 0.0) + probability / 16
        distribution[landing] = distribution.get(landing, 0.0) + 6 / 16
        return distribution
    return {landing: 1.0}


def transition_matrix(dice_size: int) -> list[list[float]]:
    """Build the transition matrix over the augmented state ``square * 3 + consecutive_doubles``.

    Tracking the consecutive-doubles count (0, 1 or 2 coming into a turn) lets the third
    successive double send the player straight to jail. Any move that finishes in jail resets
    the streak. State count is ``board_size * 3``; an entry is the probability of finishing in
    one state given the player started a turn in another.
    """
    states = board_size * 3
    matrix = [[0.0] * states for _ in range(states)]
    roll_probability = 1 / (dice_size * dice_size)
    for position in range(board_size):
        for doubles in range(3):
            row = matrix[position * 3 + doubles]
            for first in range(1, dice_size + 1):
                for second in range(1, dice_size + 1):
                    if first == second and doubles == 2:
                        # Third consecutive double: go directly to jail, streak resets.
                        row[JAIL * 3] += roll_probability
                        continue
                    next_doubles = doubles + 1 if first == second else 0
                    landing = (position + first + second) % board_size
                    for square, probability in resolve(landing).items():
                        streak = 0 if square == JAIL else next_doubles
                        row[square * 3 + streak] += roll_probability * probability
    return matrix


def stationary_distribution(matrix: list[list[float]]) -> list[float]:
    """Power-iterate the chain to its stationary distribution over the augmented states."""
    states = len(matrix)
    distribution = [1 / states] * states
    for _ in range(100_000):
        nxt = [0.0] * states
        for i, weight in enumerate(distribution):
            if weight:
                row = matrix[i]
                for j, probability in enumerate(row):
                    if probability:
                        nxt[j] += weight * probability
        if max(abs(a - b) for a, b in zip(nxt, distribution)) < 1e-15:
            return nxt
        distribution = nxt
    return distribution


@runner.main
def solve(*args: str) -> str:
    """Exact solution via the board's stationary distribution (no simulation, so the result is
    deterministic). Build the transition matrix over the augmented state (square, consecutive
    doubles), power-iterate to the steady state, marginalise to per-square probabilities, and
    report the three most popular squares as a six-digit modal string."""
    dice_size = runner.parse_int(args[0])

    distribution = stationary_distribution(transition_matrix(dice_size))
    square_probability = [sum(distribution[square * 3:square * 3 + 3]) for square in range(board_size)]
    ranked = sorted(range(board_size), key=lambda square: (-square_probability[square], square))
    return "".join(f"{square:02d}" for square in ranked[:3])


if __name__ == "__main__":
    raise SystemExit(solve())
