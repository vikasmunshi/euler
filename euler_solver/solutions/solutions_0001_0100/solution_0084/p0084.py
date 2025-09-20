#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 84: Monopoly Odds.

Problem Statement:
    In the game, Monopoly, the standard board is set up in the following way:

    A player starts on the GO square and adds the scores on two 6-sided dice to
    determine the number of squares they advance in a clockwise direction. Without
    any further rules we would expect to visit each square with equal probability:
    2.5%. However, landing on G2J (Go To Jail), CC (community chest), and CH (chance)
    changes this distribution.

    In addition to G2J, and one card from each of CC and CH, that orders the player
    to go directly to jail, if a player rolls three consecutive doubles, they do not
    advance the result of their 3rd roll. Instead they proceed directly to jail.

    At the beginning of the game, the CC and CH cards are shuffled. When a player
    lands on CC or CH they take a card from the top of the respective pile and,
    after following the instructions, it is returned to the bottom of the pile.
    There are sixteen cards in each pile, but for the purpose of this problem we
    are only concerned with cards that order a movement; any instruction not
    concerned with movement will be ignored and the player will remain on the
    CC/CH square.

    Community Chest (2/16 cards):
        1. Advance to GO
        2. Go to JAIL

    Chance (10/16 cards):
        1. Advance to GO
        2. Go to JAIL
        3. Go to C1
        4. Go to E3
        5. Go to H2
        6. Go to R1
        7. Go to next R (railway company)
        8. Go to next R
        9. Go to next U (utility company)
        10. Go back 3 squares.

    The heart of this problem concerns the likelihood of visiting a particular square.
    That is, the probability of finishing at that square after a roll. For this reason
    it should be clear that, with the exception of G2J for which the probability of
    finishing on it is zero, the CH squares will have the lowest probabilities, as
    5/8 request a movement to another square, and it is the final square that the
    player finishes at on each roll that we are interested in. We shall make no
    distinction between "Just Visiting" and being sent to JAIL, and we shall also
    ignore the rule about requiring a double to "get out of jail", assuming that
    they pay to get out on their next turn.

    By starting at GO and numbering the squares sequentially from 00 to 39 we can
    concatenate these two-digit numbers to produce strings that correspond with
    sets of squares.

    Statistically it can be shown that the three most popular squares, in order,
    are JAIL (6.24%) = Square 10, E3 (3.18%) = Square 24, and GO (3.09%) = Square 00.
    So these three most popular squares can be listed with the six-digit modal string:
    102400.

    If, instead of using two 6-sided dice, two 4-sided dice are used, find the
    six-digit modal string.

Solution Approach:
    Model the game as a Markov chain with 40 states representing board squares.
    Incorporate dice roll probabilities for 4-sided dice, chance/community-chest
    card effects, and special rules (G2J, three doubles in a row).

    Use linear algebra or iterative steady-state probability computation to find
    the long-term distribution of the player's position.

    Extract the three most probable squares from this distribution and format
    their indices as a six-digit concatenated string.

Answer: 101524
URL: https://projecteuler.net/problem=84
"""
from __future__ import annotations

from collections import defaultdict
from ctypes import Array, POINTER, c_int, c_longlong
from itertools import cycle
from random import randint, shuffle
from typing import Any, Callable, Dict, Generator, Iterator, List, Protocol

from euler_solver.framework import evaluate, import_c_lib, logger, register_solution, use_c_function

euler_problem: int = 84
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'dice_size': 6, 'simulations': 1000000}, 'answer': '102400'},
    {'category': 'main', 'input': {'dice_size': 4, 'simulations': 1000000}, 'answer': '101524'},
]

board: tuple[str, ...] = ('GO', 'A1', 'CC1', 'A2', 'T1', 'R1', 'B1', 'CH1', 'B2', 'B3', 'JAIL', 'C1', 'U1', 'C2', 'C3',
                          'R2', 'D1', 'CC2', 'D2', 'D3', 'FP', 'E1', 'CH2', 'E2', 'E3', 'R3', 'F1', 'F2', 'U2', 'F3',
                          'G2J', 'G1', 'G2', 'CC3', 'G3', 'R4', 'CH3', 'H1', 'T2', 'H2')
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


class BackwardMovement(Movement):
    def seek(self, position: int) -> int:
        return (position - 3 + board_size) % board_size


class NullMovement(Movement):
    def seek(self, position: int) -> int:
        return position


def card_stack(cards: list[Movement]) -> Generator[Movement, None, None]:
    shuffle(cards)
    for card in cycle(cards):
        yield card


def community_chest_cards() -> Generator[Movement, None, None]:
    cards: List[Movement] = [ForwardMovement('GO'), ForwardMovement('JAIL')] + [NullMovement()] * 14
    yield from card_stack(cards)


def chance_cards() -> Generator[Movement, None, None]:
    cards: List[Movement] = [ForwardMovement('GO'), ForwardMovement('JAIL'), ForwardMovement('C1'),
                             ForwardMovement('E3'), ForwardMovement('H2'), ForwardMovement('R1'), ForwardMovement('R'),
                             ForwardMovement('R'), ForwardMovement('U'), BackwardMovement()] + [NullMovement()] * 6
    yield from card_stack(cards)


def dice_roll(dice_size: int) -> int:
    first = randint(1, dice_size)
    second = randint(1, dice_size)
    return first + second


def c_wrapper() -> tuple[Callable, ...]:
    # Load the C library built from src/p0084.c -> libs/lib_p0084.so
    _c_lib = import_c_lib(euler_problem)

    # Bind C function: int monopoly_simulate(int dice_size, int simulations, long long* counts_out)
    _c_func = getattr(_c_lib, 'monopoly_simulate')
    _c_func.argtypes = [c_int, c_int, POINTER(c_longlong)]
    _c_func.restype = c_int

    def simulate_c(*, dice_size: int, simulations: int) -> list[tuple[float, str, int]]:
        if not isinstance(dice_size, int) or dice_size <= 0:
            raise ValueError('dice_size must be a positive integer')
        if not isinstance(simulations, int) or simulations < 0:
            raise ValueError('simulations must be a non-negative integer')

        counts_arr: Array[c_longlong] = (c_longlong * len(board))()
        rc = int(_c_func(int(dice_size), int(simulations), counts_arr))
        if rc != 0:
            raise RuntimeError(f'C simulation failed with error code {rc}')

        total = float(simulations) if simulations > 0 else 1.0
        results = []
        count: c_longlong
        for idx, count in enumerate(counts_arr):
            if count:
                percentage = 100.0 * float(count) / total
                results.append((percentage, board[idx], idx))
        # Sort descending by percentage, then by index as tiebreaker to be stable
        results.sort(key=lambda t: (-t[0], t[2]))
        return results

    return (simulate_c,)


@use_c_function(c_wrapper, 0)
def simulate(*, dice_size: int, simulations: int) -> list[tuple[float, str, int]]:
    position: int = 0
    visited_fields: Dict[str, int] = defaultdict(int)
    chance_cards_iter: Iterator[Movement] = chance_cards()
    community_chest_cards_iter: Iterator[Movement] = community_chest_cards()
    for i in range(simulations):
        position += dice_roll(dice_size)
        position %= board_size
        if board[position].startswith('CC'):
            movement = next(community_chest_cards_iter)
            position = movement.seek(position)
        elif board[position].startswith('CH'):
            movement = next(chance_cards_iter)
            position = movement.seek(position)
        elif board[position] == 'G2J':
            position = board.index('JAIL')
        visited_fields[board[position]] += 1
    results = sorted([(100 * count / simulations, field, board.index(field))
                      for field, count in visited_fields.items()], reverse=True)
    return results


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_monopoly_odds_p0084_s0(*, dice_size: int, simulations: int) -> str:
    results = simulate(dice_size=dice_size, simulations=simulations)
    return ''.join((f'{index:02d}' for percentage, field, index in results[:3]))


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
