#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 61: Cyclical Figurate Numbers [Level 3]. """
from __future__ import annotations

import enum
import functools
import math
import typing

from solver.runners import runner


def n_is_positive_integer[T](func: typing.Callable[[int], T]) -> typing.Callable[[int], T]:
    """Decorator enforcing that the wrapped nth-value function receives a positive integer."""
    @functools.wraps(func)
    def wrapper(n: int) -> T:
        if isinstance(n, int) and n > 0:
            return func(n)
        else:
            raise ValueError(f"'n' must be a positive integer, got {n}")

    return wrapper


@n_is_positive_integer
def nth_hexagonal_number(n: int) -> int:
    """Return the nth hexagonal number P(6,n) = n(2n-1)."""
    return n * (2 * n - 1)


@n_is_positive_integer
def closest_hexagonal_number(n: int) -> tuple[float, int, int]:
    """Return the inverted index for value n and the hexagonal numbers either side of it."""
    return (
        (i := ((1 + math.sqrt(1 + 8 * n)) / 4)),
        nth_hexagonal_number(math.floor(i)),
        nth_hexagonal_number(math.ceil(i)),
    )


class FigurateNumber(enum.Enum):
    """Enumeration of all figurate (polygonal) numbers.

    Each enum value represents a specific polygonal number type,
    with the value indicating the number of sides in the polygon.
    For example, TRIANGLE=3 for 3-sided polygons, SQUARE=4 for 4-sided, etc.

    This enum provides a type-safe way to reference different figurate number types
    and is used as keys in the function mapping dictionaries (p_funcs, v_funcs, c_funcs).
    """

    TRIANGLE = 3
    SQUARE = 4
    PENTAGONAL = 5
    HEXAGONAL = 6
    HEPTAGONAL = 7
    OCTAGONAL = 8

    def __str__(self) -> str:
        """Return the enum member as a title-cased string."""
        return self.name.title()


@n_is_positive_integer
def nth_triangle_number(n: int) -> int:
    """Return the nth triangle number P(3,n) = n(n+1)/2."""
    return n * (n + 1) // 2


@n_is_positive_integer
def closest_triangle_number(n: int) -> tuple[float, int, int]:
    """Return the inverted index for value n and the triangle numbers either side of it."""
    return (
        (i := ((-1 + math.sqrt(1 + 8 * n)) / 2)),
        nth_triangle_number(math.floor(i)),
        nth_triangle_number(math.ceil(i)),
    )


@n_is_positive_integer
def nth_pentagonal_number(n: int) -> int:
    """Return the nth pentagonal number P(5,n) = n(3n-1)/2."""
    return n * (3 * n - 1) // 2


@n_is_positive_integer
def closest_pentagonal_number(n: int) -> tuple[float, int, int]:
    """Return the inverted index for value n and the pentagonal numbers either side of it."""
    return (
        (i := ((1 + math.sqrt(1 + 24 * n)) / 6)),
        nth_pentagonal_number(math.floor(i)),
        nth_pentagonal_number(math.ceil(i)),
    )


@n_is_positive_integer
def nth_square_number(n: int) -> int:
    """Return the nth square number P(4,n) = n^2."""
    return n ** 2


@n_is_positive_integer
def closest_square_number(n: int) -> tuple[float, int, int]:
    """Return the inverted index for value n and the square numbers either side of it."""
    return ((i := math.sqrt(n)), nth_square_number(math.floor(i)), nth_square_number(math.ceil(i)))


@n_is_positive_integer
def nth_octagonal_number(n: int) -> int:
    """Return the nth octagonal number P(8,n) = n(3n-2)."""
    return n * (3 * n - 2)


@n_is_positive_integer
def closest_octagonal_number(n: int) -> tuple[float, int, int]:
    """Return the inverted index for value n and the octagonal numbers either side of it."""
    return (
        (i := ((2 + math.sqrt(4 + 12 * n)) / 6)),
        nth_octagonal_number(math.floor(i)),
        nth_octagonal_number(math.ceil(i)),
    )


@n_is_positive_integer
def nth_heptagonal_number(n: int) -> int:
    """Return the nth heptagonal number P(7,n) = n(5n-3)/2."""
    return n * (5 * n - 3) // 2


@n_is_positive_integer
def closest_heptagonal_number(n: int) -> tuple[float, int, int]:
    """Return the inverted index for value n and the heptagonal numbers either side of it."""
    return (
        (i := ((3 + math.sqrt(9 + 40 * n)) / 10)),
        nth_heptagonal_number(math.floor(i)),
        nth_heptagonal_number(math.ceil(i)),
    )


c_funcs: dict[FigurateNumber, typing.Callable[[int], tuple[float, int, int]]] = {
    FigurateNumber.TRIANGLE: closest_triangle_number,
    FigurateNumber.SQUARE: closest_square_number,
    FigurateNumber.PENTAGONAL: closest_pentagonal_number,
    FigurateNumber.HEXAGONAL: closest_hexagonal_number,
    FigurateNumber.HEPTAGONAL: closest_heptagonal_number,
    FigurateNumber.OCTAGONAL: closest_octagonal_number,
}
p_funcs: dict[FigurateNumber, typing.Callable[[int], int]] = {
    FigurateNumber.TRIANGLE: nth_triangle_number,
    FigurateNumber.SQUARE: nth_square_number,
    FigurateNumber.PENTAGONAL: nth_pentagonal_number,
    FigurateNumber.HEXAGONAL: nth_hexagonal_number,
    FigurateNumber.HEPTAGONAL: nth_heptagonal_number,
    FigurateNumber.OCTAGONAL: nth_octagonal_number,
}


def p_gen(p_num: FigurateNumber, min_value: int = 0, max_value: int = 2 ** 32) -> typing.Generator[int, None, None]:
    """Yield the figurate numbers of one type within [min_value, max_value], seeded via the inverse."""
    p_func: typing.Callable[[int], int] = p_funcs[p_num]
    c_func: typing.Callable[[int], tuple[float, int, int]] = c_funcs[p_num]
    start_num: int = math.floor(c_func(min_value)[0])
    stop_num: int = math.ceil(c_func(max_value)[0]) + 1
    for i in range(start_num, stop_num):
        if min_value <= (p := p_func(i)) <= max_value:
            yield p


def find_cyclic_paths(
        start: int,
        current: int,
        path: list[int],
        visited: set[int],
        number_mapping: dict[int, list[int]],
        target_length: int,
) -> list[tuple[int, ...]]:
    """Backtracking DFS returning every length-target_length path that closes back to the start."""
    if len(path) == target_length:
        if current % 100 == start // 100:
            return [tuple(path[:])]
        return []
    result: list[tuple[int, ...]] = []
    for next_num in number_mapping.get(current, []):
        if next_num not in visited:
            path.append(next_num)
            visited.add(next_num)
            result.extend(find_cyclic_paths(start, next_num, path, visited, number_mapping, target_length))
            path.pop()
            visited.remove(next_num)
    return [tuple(r) for r in result]


def verify_polygon_types(chain: tuple[int, ...], p_numbers: dict[FigurateNumber, set[int]]) -> bool:
    """True if the chain covers every polygon type once, handling numbers belonging to several families."""
    figurate_in_chain: dict[FigurateNumber, list[int]] = {k: [n for n in chain if n in v] for k, v in p_numbers.items()}
    if any((len(n) == 0 for n in figurate_in_chain.values())):
        return False
    figurate_in_chain_rev: dict[int, list[FigurateNumber]] = {}
    for k_f, v_f in figurate_in_chain.items():
        for n_f in v_f:
            figurate_in_chain_rev.setdefault(n_f, []).append(k_f)
    for k_r, v_r in figurate_in_chain_rev.items():
        if len(v_r) > 1:
            if all((len(f) == 1 for n_r in v_r if (f := figurate_in_chain[n_r]))):
                return False
    return True


@runner.main
def solve(*args: str) -> str:
    """Model the digit-linking rule as a directed sparse graph over 4-digit figurate numbers, then
    DFS for length-cycles covering all polygon types; O(V^length) worst case, near-instant in practice
    given the short successor lists."""
    length = runner.parse_int(args[0])

    min_value: int = 10 ** 3
    max_value: int = 10 ** 4 - 1
    generator_funcs: dict[FigurateNumber, typing.Generator[int, None, None]] = {
        (p_num := FigurateNumber(n)): p_gen(p_num=FigurateNumber(p_num), min_value=min_value, max_value=max_value)
        for n in range(3, length + 3)
    }
    p_numbers: dict[FigurateNumber, set[int]] = {p_num: set(gen) for p_num, gen in generator_funcs.items()}
    number_to_next_graph: dict[int, list[int]] = {n: list() for vals in p_numbers.values() for n in vals}
    for next_number in number_to_next_graph.keys():
        first_two_digits = next_number // 100
        for previous_number, successor_list in number_to_next_graph.items():
            if first_two_digits == previous_number % 100:
                successor_list.append(next_number)
    cyclic_paths: set[tuple[int, ...]] = set()
    for start_num in (k for k, v in number_to_next_graph.items() if v):
        for path in find_cyclic_paths(start_num, start_num, [start_num], {start_num}, number_to_next_graph, length):
            cyclic_paths.add(tuple(sorted(path)))
    valid_cyclic_paths: list = sorted((path for path in cyclic_paths if verify_polygon_types(path, p_numbers)), key=sum)
    if runner.show:
        from pprint import pprint

        for valid_cyclic_path in valid_cyclic_paths:
            figurates = {n: tuple((str(k) for k, v in p_numbers.items() if n in v)) for n in valid_cyclic_path}
            print(f"length={length!r} {figurates}")
            pprint(figurates)
    return str([
        (len_paths := len(valid_cyclic_paths)),
        sum(valid_cyclic_paths[0]) if len_paths == 1 else [sum(path) for path in valid_cyclic_paths],
    ])


if __name__ == "__main__":
    raise SystemExit(solve())
