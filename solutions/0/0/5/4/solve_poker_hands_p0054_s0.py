#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Migrated from:
  file: euler_solver/solutions/solutions_0001_0100/solution_0054/p0054.py
  func: solve_poker_hands_p0054_s0
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum
from functools import cached_property
from pathlib import Path
from sys import argv
from typing import Any, Dict, Tuple, Union, cast

VALUES = "23456789TJQKA"


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


SUITS = "CDHS"


SUIT_ORDER: Dict[str, int] = {"C": 0, "D": 1, "H": 2, "S": 3}


@dataclass
class PokerHand:
    cards: Tuple[str, str, str, str, str]
    values: Tuple[int, int, int, int, int] = field(init=False, default=None)
    suits: Tuple[str, str, str, str, str] = field(init=False, default=None)

    def __post_init__(self) -> None:
        if not isinstance(self.cards, (list, tuple)) or len(self.cards) != 5:
            raise ValueError("Cards must be a list or tuple of exactly 5 cards")
        for card in self.cards:
            if any((not isinstance(card, str), len(card) != 2, card[0] not in VALUES, card[1] not in SUITS)):
                raise ValueError(f"Invalid card: {card}")
        if isinstance(self.cards, list):
            self.cards = cast(Tuple[str, str, str, str, str], tuple(self.cards))
        if self.values is None:
            self.values = (
                VALUES.index(self.cards[0][0]),
                VALUES.index(self.cards[1][0]),
                VALUES.index(self.cards[2][0]),
                VALUES.index(self.cards[3][0]),
                VALUES.index(self.cards[4][0]),
            )
        if self.suits is None:
            self.suits = (self.cards[0][1], self.cards[1][1], self.cards[2][1], self.cards[3][1], self.cards[4][1])

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


def get_text_file(url: str) -> str:
    """Return the contents of a file from the 'resources' directory."""
    local_filename: str = "resources" + "/" + url.split("/")[-1].split("?")[0]
    return (Path(__file__).parent / local_filename).read_text()


def solve(*, file_url: str) -> int:
    plays = (
        (
            PokerHand(cast(tuple[str, str, str, str, str], cards[:5])),
            PokerHand(cast(tuple[str, str, str, str, str], cards[5:])),
        )
        for line in get_text_file(file_url).splitlines()
        if (cards := line.split())
    )
    return sum((player_1_hand.hand_rank > player_2_hand.hand_rank for player_1_hand, player_2_hand in plays))


def main() -> int:
    print(solve(file_url=str(argv[1])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
