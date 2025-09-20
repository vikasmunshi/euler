#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 54: Poker Hands.

Problem Statement:
    In the card game poker, a hand consists of five cards and are ranked, from lowest
    to highest, in the following way:

        High Card: Highest value card.
        One Pair: Two cards of the same value.
        Two Pairs: Two different pairs.
        Three of a Kind: Three cards of the same value.
        Straight: All cards are consecutive values.
        Flush: All cards of the same suit.
        Full House: Three of a kind and a pair.
        Four of a Kind: Four cards of the same value.
        Straight Flush: All cards are consecutive values of same suit.
        Royal Flush: Ten, Jack, Queen, King, Ace, in same suit.

    The cards are valued in the order:
    2, 3, 4, 5, 6, 7, 8, 9, 10, Jack, Queen, King, Ace.

    If two players have the same ranked hands then the rank made up of the highest
    value wins; for example, a pair of eights beats a pair of fives. But if two ranks
    tie, for example, both players have a pair of queens, then highest cards in each
    hand are compared; if the highest cards tie then the next highest cards are
    compared, and so on.

    Consider the following five hands dealt to two players:

        Hand 1:
            Player 1: 5H 5C 6S 7S KD (Pair of Fives)
            Player 2: 2C 3S 8S 8D TD (Pair of Eights)
            Winner: Player 2

        Hand 2:
            Player 1: 5D 8C 9S JS AC (Highest card Ace)
            Player 2: 2C 5C 7D 8S QH (Highest card Queen)
            Winner: Player 1

        Hand 3:
            Player 1: 2D 9C AS AH AC (Three Aces)
            Player 2: 3D 6D 7D TD QD (Flush with Diamonds)
            Winner: Player 2

        Hand 4:
            Player 1: 4D 6S 9H QH QC (Pair of Queens, Highest card Nine)
            Player 2: 3D 6D 7H QD QS (Pair of Queens, Highest card Seven)
            Winner: Player 1

        Hand 5:
            Player 1: 2H 2D 4C 4D 4S (Full House with Three Fours)
            Player 2: 3C 3D 3S 9S 9D (Full House with Three Threes)
            Winner: Player 1

    The file, poker.txt, contains one-thousand random hands dealt to two players. Each
    line of the file contains ten cards (separated by a single space): the first five
    are Player 1's cards and the last five are Player 2's cards. You can assume that
    all hands are valid, each player's hand is in no specific order, and in each hand
    there is a clear winner.

    How many hands does Player 1 win?

Solution Approach:
    Parse and rank poker hands using combinatorics and hand classification rules.
    Implement poker hand ranking hierarchy, compare rank and tie-breakers.
    Efficient string parsing and comparison. Counting wins with file input.
    Expected complexity: O(number_of_hands) in file.

Answer: 376
URL: https://projecteuler.net/problem=54
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum
from functools import cached_property
from typing import Any, Dict, Tuple, Union, cast

from euler_solver.framework import evaluate, get_text_file, logger, register_solution

euler_problem: int = 54
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'file_url': 'https://projecteuler.net/resources/documents/0054_poker.txt'},
     'answer': 376},
]

problem_number: int = 54
VALUES = '23456789TJQKA'
SUITS = 'CDHS'
SUIT_ORDER: Dict[str, int] = {'C': 0, 'D': 1, 'H': 2, 'S': 3}


class PokerRank(IntEnum):
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
    rank: PokerRank
    tie_breakers: Union[int, Tuple[int, ...]]

    def __gt__(self, other: Any) -> bool:
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
    cards: Tuple[str, str, str, str, str]
    values: Tuple[int, int, int, int, int] = field(init=False, default=None)  # type: ignore[assignment]
    suits: Tuple[str, str, str, str, str] = field(init=False, default=None)  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if not isinstance(self.cards, (list, tuple)) or len(self.cards) != 5:
            raise ValueError('Cards must be a list or tuple of exactly 5 cards')
        for card in self.cards:
            if any((not isinstance(card, str), len(card) != 2, card[0] not in VALUES, card[1] not in SUITS)):
                raise ValueError(f'Invalid card: {card}')
        if isinstance(self.cards, list):
            self.cards = cast(Tuple[str, str, str, str, str], tuple(self.cards))  # type: ignore[unreachable]
        if self.values is None:
            self.values = (VALUES.index(self.cards[0][0]), VALUES.index(self.cards[1][0]),  # type: ignore[unreachable]
                           VALUES.index(self.cards[2][0]), VALUES.index(self.cards[3][0]),
                           VALUES.index(self.cards[4][0]))
        if self.suits is None:
            self.suits = (self.cards[0][1], self.cards[1][1], self.cards[2][1],  # type: ignore[unreachable]
                          self.cards[3][1], self.cards[4][1])

    @cached_property
    def hand_rank(self) -> HandRank:
        values, suits = (self.values, self.suits)
        is_straight = len(set(values)) == 5 and max(values) - min(values) == 4
        is_flush = len(set(suits)) == 1
        if is_straight and is_flush:
            if min(values) == 8:
                return HandRank(PokerRank.ROYAL_FLUSH, SUIT_ORDER[suits[0]])
            return HandRank(PokerRank.STRAIGHT_FLUSH, max(values))
        value_counts = tuple(sorted([(self.values.count(v), v) for v in set(self.values)], reverse=True))
        if value_counts[0][0] == 4:
            return HandRank(PokerRank.FOUR_OF_A_KIND, (value_counts[0][1], value_counts[1][1]))
        if value_counts[0][0] == 3 and value_counts[1][0] == 2:
            return HandRank(PokerRank.FULL_HOUSE, (value_counts[0][1], value_counts[1][1]))
        if is_flush:
            return HandRank(PokerRank.FLUSH, tuple(sorted(values, reverse=True)))
        if is_straight:
            return HandRank(PokerRank.STRAIGHT, max(values))
        if value_counts[0][0] == 3:
            return HandRank(PokerRank.THREE_OF_A_KIND,
                            (value_counts[0][1], *sorted([v for v in values if v != value_counts[0][1]], reverse=True)))
        if len(value_counts) >= 2 and value_counts[0][0] == 2 and (value_counts[1][0] == 2):
            high_pair, low_pair = sorted([value_counts[0][1], value_counts[1][1]], reverse=True)
            return HandRank(PokerRank.TWO_PAIRS,
                            (high_pair, low_pair, [v for v in values if v != high_pair and v != low_pair][0]))
        if value_counts[0][0] == 2:
            return HandRank(PokerRank.ONE_PAIR,
                            (value_counts[0][1], *sorted([v for v in values if v != value_counts[0][1]], reverse=True)))
        return HandRank(PokerRank.HIGH_CARD, tuple(sorted(values, reverse=True)))


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_poker_hands_p0054_s0(*, file_url: str) -> int:
    plays = ((PokerHand(cast(tuple[str, str, str, str, str], cards[:5])),
              PokerHand(cast(tuple[str, str, str, str, str], cards[5:]))) for line in
             get_text_file(file_url).splitlines() if (cards := line.split()))
    return sum((player_1_hand.hand_rank > player_2_hand.hand_rank for player_1_hand, player_2_hand in plays))


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
