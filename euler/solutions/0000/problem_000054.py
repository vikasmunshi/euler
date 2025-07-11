#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Solution to Project Euler problem 54: Poker hands

Problem Statement:
In the card game poker, a hand consists of five cards and are ranked, from lowest to highest, in the following way:

- High Card: Highest value card.
- One Pair: Two cards of the same value.
- Two Pairs: Two different pairs.
- Three of a Kind: Three cards of the same value.
- Straight: All cards are consecutive values.
- Flush: All cards of the same suit.
- Full House: Three of a kind and a pair.
- Four of a Kind: Four cards of the same value.
- Straight Flush: All cards are consecutive values of same suit.
- Royal Flush: Ten, Jack, Queen, King, Ace, in same suit.

The cards are valued in the order:
2, 3, 4, 5, 6, 7, 8, 9, 10, Jack, Queen, King, Ace.

If two players have the same ranked hands then the rank made up of the highest value wins; 
for example, a pair of eights beats a pair of fives (see example 1 below). But if two ranks tie, 
for example, both players have a pair of queens, then highest cards in each hand are compared; 
if the highest cards tie then the next highest cards are compared, and so on.
Consider the following five hands dealt to two players:

Hand  | Player 1          | Player 2          | Winner
------|-------------------|-------------------|--------
1     | 5H 5C 6S 7S KD    | 2C 3S 8S 8D TD    | Player 2
      | (Pair of Fives)   | (Pair of Eights)  |
2     | 5D 8C 9S JS AC    | 2C 5C 7D 8S QH    | Player 1
      | (Highest: Ace)    | (Highest: Queen)  |
3     | 2D 9C AS AH AC    | 3D 6D 7D TD QD    | Player 2
      | (Three Aces)      | (Flush with Diamonds)|
4     | 4D 6S 9H QH QC    | 3D 6D 7H QD QS    | Player 1
      | (Queens, Nine high)| (Queens, Seven high)|
5     | 2H 2D 4C 4D 4S    | 3C 3D 3S 9S 9D    | Player 1
      | (Full House: 4s/2s)| (Full House: 3s/9s)|

The file, poker.txt, contains one-thousand random hands dealt to two players. Each line of the 
file contains ten cards (separated by a single space): the first five are Player 1's cards and 
the last five are Player 2's cards. You can assume that all hands are valid (no invalid characters 
or repeated cards), each player's hand is in no specific order, and in each hand there is a clear winner.

How many hands does Player 1 win?

Solution Approach:
This solution implements an object-oriented poker hand evaluator with three main components:

1. PokerRank - An enumeration defining the hierarchy of poker hand categories
2. HandRank - A class that encapsulates both the hand category and tiebreaking values
3. PokerHand - A class that parses card strings, evaluates hand strength, and enables comparison

The implementation works as follows:
- Parse each line of the input file into two hands of five cards each
- For each hand, determine its poker rank and appropriate tiebreaking values
- Compare the hands directly using overloaded comparison operators
- Count how many times Player 1's hand ranks higher than Player 2's

The evaluation algorithm efficiently identifies hand types from highest to lowest rank,
and applies comprehensive tiebreaking logic according to standard poker rules.

Test Cases:
- For the provided poker.txt file: Player 1 wins 376 hands

URL: https://projecteuler.net/problem=54
Answer: 376
"""
from dataclasses import dataclass, field
from enum import IntEnum
from functools import cached_property
from typing import Tuple, Dict, Union, Any

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol
from euler.utils import get_text_file

problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={'file_url': 'https://projecteuler.net/resources/documents/0054_poker.txt'}, answer=376, ),
]

# Card values and ranks
VALUES = '23456789TJQKA'
SUITS = 'CDHS'
SUIT_ORDER: Dict[str, int] = {'C': 0, 'D': 1, 'H': 2, 'S': 3}


class PokerRank(IntEnum):
    """
    Enum representing standard poker hand rankings from lowest to highest.

    Each rank is assigned an integer value with higher values representing stronger hands.
    These values provide a simple way to compare different hand categories.
    """
    HIGH_CARD = 0
    ONE_PAIR = 1
    TWO_PAIRS = 2
    THREE_OF_A_KIND = 3
    STRAIGHT = 4
    FLUSH = 5
    FULL_HOUSE = 6
    FOUR_OF_A_KIND = 7
    STRAIGHT_FLUSH = 8
    ROYAL_FLUSH = 9


@dataclass
class HandRank:
    """Class representing a poker hand rank with comprehensive tiebreaking capabilities.

    This class encapsulates both the primary classification of a poker hand (e.g., Flush,
    Straight, etc.) and the secondary tiebreaking values that determine the winner when
    two hands share the same primary rank.

    Attributes:
        rank: The PokerRank enum value representing the hand's classification (0-9,
              where 9 is Royal Flush)
        tie_breakers: Value(s) used to break ties between hands of the same rank.
            This can be either a single integer (for simpler hands like Straight) or
            a tuple of integers (for more complex hands like Two Pairs). Specifically:
            - High Card: Tuple of all 5 card values in descending order
            - One Pair: Tuple of (pair value, high kicker, middle kicker, low kicker)
            - Two Pairs: Tuple of (high pair value, low pair value, kicker value)
            - Three of a Kind: Tuple of (triplet value, high kicker, low kicker)
            - Straight: Highest card value in the straight
            - Flush: Tuple of all 5 card values in descending order
            - Full House: Tuple of (triplet value, pair value)
            - Four of a Kind: Tuple of (quads value, kicker value)
            - Straight Flush: Highest card value in the straight
            - Royal Flush: Value based on suit hierarchy where
              Spades(S) > Hearts(H) > Diamonds(D) > Clubs(C)
    """
    rank: PokerRank
    tie_breakers: Union[int, Tuple[int, ...]]

    def __gt__(self, other: Any) -> bool:
        """Compare two hand ranks to determine which is higher, according to poker rules.

        This method implements the standard poker hand comparison logic:
        1. First, compare the primary rank category (e.g., Flush beats Straight)
        2. If ranks are identical, compare tiebreakers in order of importance:
           - For pairs: compare pair values first, then kicker values in descending order
           - For straights/straight flushes: compare the highest card value
           - For flushes: compare cards in descending order until a difference is found
           - For full houses: compare the triplet value, then the pair value
           - For four of a kind: compare the quad value, then the kicker

        Args:
            other: Another HandRank object to compare against

        Returns:
            bool: True if this hand ranks higher than the other hand
        """
        if not isinstance(other, HandRank):
            return NotImplemented
        if self.rank != other.rank:
            return self.rank > other.rank
        if isinstance(self.tie_breakers, int) and isinstance(other.tie_breakers, int):
            return self.tie_breakers > other.tie_breakers
        if isinstance(self.tie_breakers, tuple) and isinstance(other.tie_breakers, tuple):
            if len(self.tie_breakers) == len(other.tie_breakers):
                return self.tie_breakers > other.tie_breakers
        return NotImplemented


@dataclass
class PokerHand:
    """Class representing a 5-card poker hand with comprehensive evaluation capabilities.

    This class parses, validates, and evaluates a standard 5-card poker hand. Each card
    is represented as a 2-character string where the first character indicates the card's
    value (2-9, T, J, Q, K, A) and the second character represents the suit (H, D, S, C).

    Attributes:
        cards: Tuple of 5 card strings (e.g., ('5H', 'JC', 'AH', '9S', 'KD'))
        values: Tuple of integer values for each card, automatically calculated based on
                the position in VALUES constant (0-12, where A=12)
        suits: Tuple of suit characters for each card, automatically extracted from card strings
    """
    cards: Tuple[str, str, str, str, str]
    values: Tuple[int, int, int, int, int] = field(init=False, default=None)
    suits: Tuple[str, str, str, str, str] = field(init=False, default=None)

    def __post_init__(self):
        if not isinstance(self.cards, (list, tuple)) or len(self.cards) != 5:
            raise ValueError('Cards must be a list or tuple of exactly 5 cards')
        for card in self.cards:
            if any((not isinstance(card, str), len(card) != 2, card[0] not in VALUES, card[1] not in SUITS,)):
                raise ValueError(f'Invalid card: {card}')
        if isinstance(self.cards, list):
            self.cards = cast(Tuple[str, str, str, str, str], tuple(self.cards))
        if self.values is None:
            self.values = (VALUES.index(self.cards[0][0]), VALUES.index(self.cards[1][0]),
                           VALUES.index(self.cards[2][0]), VALUES.index(self.cards[3][0]),
                           VALUES.index(self.cards[4][0]))
        if self.suits is None:
            self.suits = (self.cards[0][1], self.cards[1][1], self.cards[2][1], self.cards[3][1], self.cards[4][1])

    @cached_property
    def hand_rank(self) -> HandRank:
        """Evaluates the poker hand and returns its rank with appropriate tiebreakers.

        This method analyzes the hand to determine its poker ranking and tiebreaking values.
        The evaluation methodically checks for each hand type from highest to lowest ranking:
        Royal Flush → Straight Flush → Four of a Kind → Full House → Flush → Straight →
        Three of a Kind → Two Pairs → One Pair → High Card.

        For each hand type, appropriate tiebreaking values are calculated and included in the
        returned HandRank object to resolve ties when comparing hands of the same rank.
        The evaluation uses an efficient approach that minimizes redundant calculations.

        Returns:
            HandRank: An object containing the hand's rank category and tiebreaking values
        """
        values, suits = self.values, self.suits

        # Check for straight and flush
        is_straight = len(set(values)) == 5 and max(values) - min(values) == 4
        is_flush = len(set(suits)) == 1

        # Royal/Straight Flush
        if is_straight and is_flush:
            if min(values) == 8:  # Royal Flush, VALUES.index('T') = 8
                # Use suit as the tiebreaker, with - Clubs < Diamonds < Hearts < Spades
                # SUIT_ORDER maps C->0, D->1, H->2, S->3
                return HandRank(PokerRank.ROYAL_FLUSH, SUIT_ORDER[suits[0]])
            return HandRank(PokerRank.STRAIGHT_FLUSH, max(values))  # Straight Flush

        value_counts = tuple(sorted([(self.values.count(v), v) for v in set(self.values)], reverse=True))

        # Four of a kind
        if value_counts[0][0] == 4:
            return HandRank(PokerRank.FOUR_OF_A_KIND, (value_counts[0][1], value_counts[1][1]))

        # Full House
        if value_counts[0][0] == 3 and value_counts[1][0] == 2:
            return HandRank(PokerRank.FULL_HOUSE, (value_counts[0][1], value_counts[1][1]))

        # Flush
        if is_flush:
            return HandRank(PokerRank.FLUSH, tuple(sorted(values, reverse=True)))

        # Straight
        if is_straight:
            return HandRank(PokerRank.STRAIGHT, max(values))

        # Three of a kind
        if value_counts[0][0] == 3:
            return HandRank(PokerRank.THREE_OF_A_KIND,
                            (value_counts[0][1], *sorted([v for v in values if v != value_counts[0][1]], reverse=True)))

        # Two pairs
        if len(value_counts) >= 2 and value_counts[0][0] == 2 and value_counts[1][0] == 2:
            high_pair, low_pair = sorted([value_counts[0][1], value_counts[1][1]], reverse=True)
            return HandRank(PokerRank.TWO_PAIRS,
                            (high_pair, low_pair, [v for v in values if v != high_pair and v != low_pair][0]))

        # One pair
        if value_counts[0][0] == 2:
            return HandRank(PokerRank.ONE_PAIR,
                            (value_counts[0][1], *sorted([v for v in values if v != value_counts[0][1]], reverse=True)))

        # High card
        return HandRank(PokerRank.HIGH_CARD, tuple(sorted(values, reverse=True)))


def solution(*, file_url: str) -> int:
    """
    Count how many poker hands Player 1 wins out of 1000 dealt hands.

    This function analyzes poker hands from the provided file, evaluates each hand
    according to standard poker rules, and determines how many times Player 1 wins.
    It uses a comprehensive poker hand evaluation system that handles all hand types
    and tiebreaking situations.

    Args:
        file_url: URL to the text file containing 1000 poker hand pairs

    Returns:
        The number of hands won by Player 1

    Examples:
        >>> solution(file_url='https://projecteuler.net/resources/documents/0054_poker.txt')
        376
    """

    plays = ((PokerHand(cast(tuple[str, str, str, str, str], cards[:5])),
              PokerHand(cast(tuple[str, str, str, str, str], cards[5:])),)
             for line in get_text_file(file_url).splitlines() if (cards := line.split()))
    return sum(player_1_hand.hand_rank > player_2_hand.hand_rank for player_1_hand, player_2_hand in plays)


if __name__ == '__main__':
    # This block is executed when the Python module is run directly.
    # It evaluates the solution function to ensure its correctness against test cases.

    # Importing required modules: `module_main` manages how the solution is invoked and tested,
    # while `cast` helps with type safety in passing the solution as a `SolutionProtocol`.
    from typing import cast
    from euler.evaluator import module_main

    # The `module_main` function handles the evaluation process by:
    # 1. Extracting the problem number from the file name for contextual usage.
    # 2. Accepting command-line arguments to configure execution, e.g., timeout or threading options.
    # 3. Running the `solution` function for all test cases defined in `problem_args_list`.
    # 4. Outputting the test results, including details such as whether the test passed/failed and time taken.
    # 5. Returning an appropriate exit code (exit code 0 indicates success, non-zero for failures).

    # The `SystemExit` ensures the program exits with the exit code returned by `module_main`.
    raise SystemExit(module_main(module_name=__file__,
                                 solution=cast(SolutionProtocol, solution),
                                 args_list=problem_args_list))
