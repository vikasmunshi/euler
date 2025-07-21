#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
Solution to Project Euler problem 84:

Problem Statement:
In the game, Monopoly, the standard board is set up in the following way:
    <see the problem definition at https://projecteuler.net/problem=84>
A player starts on the GO square and adds the scores on two 6-sided dice to determine the number of squares they
advance in a clockwise direction. Without any further rules we would expect to visit each square with equal
probability: 2.5%. However, landing on G2J (Go To Jail), CC (community chest), and CH (chance) changes this
distribution.

In addition to G2J, and one card from each of CC and CH, that orders the player to go directly to jail, if a player
rolls three consecutive doubles, they do not advance the result of their 3rd roll. Instead they proceed directly to
jail.

At the beginning of the game, the CC and CH cards are shuffled. When a player lands on CC or CH they take a card from
the top of the respective pile and, after following the instructions, it is returned to the bottom of the pile.
There are sixteen cards in each pile, but for the purpose of this problem we are only concerned with cards that order a
movement; any instruction not concerned with movement will be ignored and the player will remain on the CC/CH square.

• Community Chest (2/16 cards):
Advance to GO
• Go to JAIL
• Chance (10/16 cards):
Advance to GO
• Go to JAIL
• Go to C1
• Go to E3
• Go to H2
• Go to R1
• Go to next R (railway company)
• Go to next R
• Go to next U (utility company)
• Go back 3 squares.

The heart of this problem concerns the likelihood of visiting a particular square. That is, the probability of
finishing at that square after a roll. For this reason it should be clear that, with the exception of G2J for which the
probability of finishing on it is zero, the CH squares will have the lowest probabilities, as 5/8 request a movement to
another square, and it is the final square that the player finishes at on each roll that we are interested in. We shall
make no distinction between "Just Visiting" and being sent to JAIL, and we shall also ignore the rule about requiring a
double to "get out of jail", assuming that they pay to get out on their next turn.

By starting at GO and numbering the squares sequentially from 00 to 39 we can concatenate these two-digit numbers to
produce strings that correspond with sets of squares.

Statistically it can be shown that the three most popular squares, in order, are
AIL (6.24%) = Square 10, E3 (3.18%) = Square 24, and GO (3.09%) = Square 00.
So these three most popular squares can be listed with the six-digit modal string: 102400.

If, instead of using two 6-sided dice, two 4-sided dice are used, find the six-digit modal string.

Solution Approach:
The solution uses a Monte Carlo simulation to estimate the probabilities of landing on each square:
1. We simulate 1 million dice rolls and movements on the Monopoly board
2. The board is represented as a tuple of square names with corresponding indices
3. Custom Movement classes handle different types of movements (forward, backward, null)
4. Card stacks (Chance and Community Chest) are simulated with random shuffling
5. After simulation, we calculate the frequency of landing on each square
6. Finally, we return the six-digit string formed by the indices of the three most frequently visited squares

Note: The solution ignores the rule about three consecutive doubles sending a player to jail for simplification

Test Cases:
- With 6-sided dice: '102400' (JAIL=10, E3=24, GO=00)
- With 4-sided dice: '101524' (JAIL=10, GO=15, E3=24)

URL: https://projecteuler.net/problem=84
Answer: 101524
"""
from collections import defaultdict
from itertools import cycle
from random import randint, shuffle
from typing import Dict, Generator, Iterator, List, Tuple

from euler.evaluator import evaluate_solutions, register_solution
from euler.types import ProblemArgs, ProblemArgsList

# The problem number from Project Euler (https://projecteuler.net/problem=84)
problem_number: int = 84

# Define the test cases for validating the solution
problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={'dice_size': 6, 'simulations': 1 * 10 ** 6}, answer='102400', ),
    ProblemArgs(kwargs={'dice_size': 4, 'simulations': 1 * 10 ** 6}, answer='101524', ),
]

board: Tuple[str, ...] = ('GO', 'A1', 'CC1', 'A2', 'T1', 'R1', 'B1', 'CH1', 'B2', 'B3', 'JAIL', 'C1', 'U1', 'C2',
                          'C3', 'R2', 'D1', 'CC2', 'D2', 'D3', 'FP', 'E1', 'CH2', 'E2', 'E3', 'R3', 'F1', 'F2',
                          'U2', 'F3', 'G2J', 'G1', 'G2', 'CC3', 'G3', 'R4', 'CH3', 'H1', 'T2', 'H2',)
board_size: int = len(board)


class Movement:
    """Base class for all movement operations on the Monopoly board."""

    def seek(self, position: int) -> int:
        """Calculate the new position after applying this movement.

        Args:
            position: Current position on the board

        Returns:
            New position after movement
        """
        raise NotImplementedError()


class ForwardMovement(Movement):
    """Movement that advances forward to the first square starting with the given prefix."""

    def __init__(self, prefix: str) -> None:
        """Initialize with the prefix to search for.

        Args:
            prefix: The prefix of the square name to move to
        """
        self._prefix = prefix

    def seek(self, position: int) -> int:
        """Find the next square with the matching prefix, moving forward.

        Args:
            position: Current position on the board

        Returns:
            New position after moving to the first square starting with prefix
        """
        while not board[position].startswith(self._prefix):
            position += 1
            position %= board_size
        return position


class BackwardMovement(Movement):
    """Movement that moves back 3 squares from the current position."""

    def seek(self, position: int) -> int:
        """Move back 3 squares from the current position.

        Args:
            position: Current position on the board

        Returns:
            New position after moving back 3 squares
        """
        return (position - 3 + board_size) % board_size


class NullMovement(Movement):
    """Movement that doesn't change the current position (stays in place)."""

    def seek(self, position: int) -> int:
        """Return the same position (no movement).

        Args:
            position: Current position on the board

        Returns:
            The same position (no change)
        """
        return position


def card_stack(cards: list[Movement]) -> Generator[Movement, None, None]:
    """Create an infinite generator of shuffled cards.

    This simulates a deck of cards that are drawn one by one and then returned to the bottom.

    Args:
        cards: List of Movement objects representing the cards in the deck

    Yields:
        Movement objects from the shuffled deck in cyclic order
    """
    shuffle(cards)
    for card in cycle(cards):
        yield card


def community_chest_cards() -> Generator[Movement, None, None]:
    """Create a generator for the Community Chest card pile.

    The Community Chest pile has 16 cards:
    - 2 cards that move the player (to GO and to JAIL)
    - 14 cards that have no movement effect

    Returns:
        Generator yielding Movement objects from the shuffled Community Chest deck
    """
    cards: List[Movement] = [ForwardMovement('GO'), ForwardMovement('JAIL')] + [NullMovement()] * 14
    yield from card_stack(cards)


def chance_cards() -> Generator[Movement, None, None]:
    """Create a generator for the Chance card pile.

    The Chance pile has 16 cards:
    - 10 cards that move the player (various destinations)
    - 6 cards that have no movement effect

    Returns:
        Generator yielding Movement objects from the shuffled Chance deck
    """
    cards: List[Movement] = [ForwardMovement('GO'), ForwardMovement('JAIL'), ForwardMovement('C1'),
                             ForwardMovement('E3'), ForwardMovement('H2'), ForwardMovement('R1'),
                             ForwardMovement('R'), ForwardMovement('R'), ForwardMovement('U'),
                             BackwardMovement(), ] + [NullMovement()] * 6
    yield from card_stack(cards)


def dice_roll(dice_size: int) -> int:
    """Simulate rolling two dice of the specified size.

    Args:
        dice_size: Number of sides on each die (e.g., 4 or 6)

    Returns:
        Sum of the two dice rolls
    """
    first = randint(1, dice_size)
    second = randint(1, dice_size)
    return first + second


# Register this function as a solution for problem #84 with test cases
@register_solution(problem_number=problem_number, args_list=problem_args_list)
def monopoly_monte_carlo_simulation(*, dice_size: int, simulations: int) -> str:
    """Simulate Monopoly games to find the most frequently visited squares.

    This function runs a Monte Carlo simulation of Monopoly games using the specified dice size.
    It tracks the frequency of landing on each square and returns the indices of the three
    most visited squares as a six-digit string.

    The simulation implements all the movement rules from the problem statement:
    - Moving according to dice rolls
    - Special actions when landing on Community Chest (CC) or Chance (CH) squares
    - Direct movement to Jail when landing on Go To Jail (G2J)

    Note: The rule about three consecutive doubles is not implemented for simplicity.

    Args:
        dice_size (int): Number of sides on each die (e.g., 4 or 6)
        simulations (int: Number of games to simulate (i.e., number of dice rolls)

    Returns:
        A six-digit string containing the indices of the three most frequently visited squares
    """
    position: int = 0
    visited_fields: Dict[str, int] = defaultdict(int)
    chance_cards_iter: Iterator[Movement] = chance_cards()
    community_chest_cards_iter: Iterator[Movement] = community_chest_cards()

    for i in range(simulations):
        # Roll dice and move player
        position += dice_roll(dice_size)
        position %= board_size

        # Handle special squares
        if board[position].startswith('CC'):
            # Community Chest square - draw a card and apply its effect
            movement = next(community_chest_cards_iter)
            position = movement.seek(position)
        elif board[position].startswith('CH'):
            # Chance square - draw a card and apply its effect
            movement = next(chance_cards_iter)
            position = movement.seek(position)
        elif board[position] == 'G2J':
            # Go To Jail square - move directly to jail
            position = board.index('JAIL')

        # Record the visit to the current square
        visited_fields[board[position]] += 1

    # Calculate percentages and sort by frequency (descending)
    results = sorted([(100 * count / simulations, field, board.index(field))
                      for field, count in visited_fields.items()],
                     reverse=True, )

    # Return the concatenated indices of the three most visited squares
    return ''.join(f'{index:02d}' for percentage, field, index in results[:3])


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(problem_number))
