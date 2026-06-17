#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 54: Poker Hands [Level 54]. """
from __future__ import annotations

import dataclasses
import enum
import functools
import typing

from solver.runners import runner

VALUES = "23456789TJQKA"


class PokerRank(enum.IntEnum):
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


@dataclasses.dataclass
class HandRank:
    """A hand's comparison key: its category plus tie-breakers ordered most-significant first."""

    rank: PokerRank
    tie_breakers: int | tuple[int, ...]

    def __gt__(self, other: typing.Any) -> bool:
        """Compare rank first, then break ties by lexicographic comparison of tie_breakers."""
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


SUITS = "CDHS"
SUIT_ORDER: dict[str, int] = {"C": 0, "D": 1, "H": 2, "S": 3}


@dataclasses.dataclass
class PokerHand:
    """Five validated cards, with values and suits decoded into numeric/character tuples."""

    cards: tuple[str, str, str, str, str]
    values: tuple[int, int, int, int, int] = dataclasses.field(init=False, default=None)  # type: ignore[assignment]
    suits: tuple[str, str, str, str, str] = dataclasses.field(init=False, default=None)  # type: ignore[assignment]

    def __post_init__(self) -> None:
        """Validate the five cards and decode each into its value rank and suit character."""
        if not isinstance(self.cards, (list, tuple)) or len(self.cards) != 5:
            raise ValueError("Cards must be a list or tuple of exactly 5 cards")
        for card in self.cards:
            if any((not isinstance(card, str), len(card) != 2, card[0] not in VALUES, card[1] not in SUITS)):
                raise ValueError(f"Invalid card: {card}")
        if isinstance(self.cards, list):
            self.cards = typing.cast(tuple[str, str, str, str, str], tuple(self.cards))  # type: ignore[unreachable]
        if self.values is None:
            self.values = (  # type: ignore[unreachable]
                VALUES.index(self.cards[0][0]),
                VALUES.index(self.cards[1][0]),
                VALUES.index(self.cards[2][0]),
                VALUES.index(self.cards[3][0]),
                VALUES.index(self.cards[4][0]),
            )
        if self.suits is None:
            self.suits = (self.cards[0][1],  # type: ignore[unreachable]
                          self.cards[1][1],
                          self.cards[2][1],
                          self.cards[3][1],
                          self.cards[4][1])

    @functools.cached_property
    def hand_rank(self) -> HandRank:
        """Classify into a HandRank via a count-sorted value table and flush/straight flags; O(1)."""
        values, suits = (self.values, self.suits)
        is_straight = len(set(values)) == 5 and max(values) - min(values) == 4
        is_flush = len(set(suits)) == 1
        if is_straight and is_flush:
            if min(values) == 8:
                return HandRank(PokerRank.ROYAL_FLUSH, SUIT_ORDER[suits[0]])
            return HandRank(PokerRank.STRAIGHT_FLUSH, max(values))
        # Sort (count, value) pairs descending so the dominant group is value_counts[0].
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
            return HandRank(
                PokerRank.THREE_OF_A_KIND,
                (value_counts[0][1], *sorted([v for v in values if v != value_counts[0][1]], reverse=True)),
            )
        if len(value_counts) >= 2 and value_counts[0][0] == 2 and (value_counts[1][0] == 2):
            high_pair, low_pair = sorted([value_counts[0][1], value_counts[1][1]], reverse=True)
            return HandRank(
                PokerRank.TWO_PAIRS, (high_pair, low_pair, [v for v in values if v != high_pair and v != low_pair][0])
            )
        if value_counts[0][0] == 2:
            return HandRank(
                PokerRank.ONE_PAIR,
                (value_counts[0][1], *sorted([v for v in values if v != value_counts[0][1]], reverse=True)),
            )
        return HandRank(PokerRank.HIGH_CARD, tuple(sorted(values, reverse=True)))


@runner.main
def solve(*args: str) -> str:
    """Reduce each hand to a comparison key and tally Player 1 wins by comparing keys; O(N) lines."""
    file_url = args[0]

    plays = (
        (
            PokerHand(typing.cast(tuple[str, str, str, str, str], tuple(cards[:5]))),
            PokerHand(typing.cast(tuple[str, str, str, str, str], tuple(cards[5:]))),
        )
        for line in runner.get_text_file(file_url).splitlines()
        if (cards := line.split())
    )
    return str(sum((player_1_hand.hand_rank > player_2_hand.hand_rank for player_1_hand, player_2_hand in plays)))


if __name__ == "__main__":
    raise SystemExit(solve())
