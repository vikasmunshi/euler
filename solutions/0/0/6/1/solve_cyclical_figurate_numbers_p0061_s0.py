#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Migrated from:
  file: euler_solver/solutions/solutions_0001_0100/solution_0061/p0061.py
  func: solve_cyclical_figurate_numbers_p0061_s0
"""

from __future__ import annotations

from enum import Enum
from functools import wraps
from math import ceil, floor, sqrt
from sys import argv, setrecursionlimit
from typing import Callable, Generator


def n_is_positive_integer[T](func: Callable[[int], T]) -> Callable[[int], T]:

    @wraps(func)
    def wrapper(n: int) -> T:
        if isinstance(n, int) and n > 0:
            return func(n)
        else:
            raise ValueError(f"'n' must be a positive integer, got {n}")

    return wrapper


@n_is_positive_integer
def nth_hexagonal_number(n: int) -> int:
    return n * (2 * n - 1)


@n_is_positive_integer
def closest_hexagonal_number(n: int) -> tuple[float, int, int]:
    return ((i := ((1 + sqrt(1 + 8 * n)) / 4)), nth_hexagonal_number(floor(i)), nth_hexagonal_number(ceil(i)))


class FigurateNumber(Enum):
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
    return n * (n + 1) // 2


@n_is_positive_integer
def closest_triangle_number(n: int) -> tuple[float, int, int]:
    return ((i := ((-1 + sqrt(1 + 8 * n)) / 2)), nth_triangle_number(floor(i)), nth_triangle_number(ceil(i)))


@n_is_positive_integer
def nth_pentagonal_number(n: int) -> int:
    return n * (3 * n - 1) // 2


@n_is_positive_integer
def closest_pentagonal_number(n: int) -> tuple[float, int, int]:
    return ((i := ((1 + sqrt(1 + 24 * n)) / 6)), nth_pentagonal_number(floor(i)), nth_pentagonal_number(ceil(i)))


@n_is_positive_integer
def nth_square_number(n: int) -> int:
    return n**2


@n_is_positive_integer
def closest_square_number(n: int) -> tuple[float, int, int]:
    return ((i := sqrt(n)), nth_square_number(floor(i)), nth_square_number(ceil(i)))


@n_is_positive_integer
def nth_octagonal_number(n: int) -> int:
    return n * (3 * n - 2)


@n_is_positive_integer
def closest_octagonal_number(n: int) -> tuple[float, int, int]:
    return ((i := ((2 + sqrt(4 + 12 * n)) / 6)), nth_octagonal_number(floor(i)), nth_octagonal_number(ceil(i)))


@n_is_positive_integer
def nth_heptagonal_number(n: int) -> int:
    return n * (5 * n - 3) // 2


@n_is_positive_integer
def closest_heptagonal_number(n: int) -> tuple[float, int, int]:
    return ((i := ((3 + sqrt(9 + 40 * n)) / 10)), nth_heptagonal_number(floor(i)), nth_heptagonal_number(ceil(i)))


c_funcs: dict[FigurateNumber, Callable[[int], tuple[float, int, int]]] = {
    FigurateNumber.TRIANGLE: closest_triangle_number,
    FigurateNumber.SQUARE: closest_square_number,
    FigurateNumber.PENTAGONAL: closest_pentagonal_number,
    FigurateNumber.HEXAGONAL: closest_hexagonal_number,
    FigurateNumber.HEPTAGONAL: closest_heptagonal_number,
    FigurateNumber.OCTAGONAL: closest_octagonal_number,
}


p_funcs: dict[FigurateNumber, Callable[[int], int]] = {
    FigurateNumber.TRIANGLE: nth_triangle_number,
    FigurateNumber.SQUARE: nth_square_number,
    FigurateNumber.PENTAGONAL: nth_pentagonal_number,
    FigurateNumber.HEXAGONAL: nth_hexagonal_number,
    FigurateNumber.HEPTAGONAL: nth_heptagonal_number,
    FigurateNumber.OCTAGONAL: nth_octagonal_number,
}


def p_gen(p_num: FigurateNumber, min_value: int = 0, max_value: int = 2**32) -> Generator[int, None, None]:
    p_func: Callable[[int], int] = p_funcs[p_num]
    c_func: Callable[[int], tuple[float, int, int]] = c_funcs[p_num]
    start_num: int = floor(c_func(min_value)[0])
    stop_num: int = ceil(c_func(max_value)[0]) + 1
    for i in range(start_num, stop_num):
        if min_value <= (p := p_func(i)) <= max_value:
            yield p


def show_solution() -> bool:
    return "--show" in argv


def find_cyclic_paths(
    start: int,
    current: int,
    path: list[int],
    visited: set[int],
    number_mapping: dict[int, list[int]],
    target_length: int,
) -> list[tuple[int, ...]]:
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


def solve(*, length: int) -> list:
    min_value: int = 10**3
    max_value: int = 10**4 - 1
    generator_funcs: dict[FigurateNumber, Generator[int, None, None]] = {
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
    valid_cyclic_paths: list[tuple[int, ...]] = sorted(
        (path for path in cyclic_paths if verify_polygon_types(path, p_numbers)), key=sum
    )
    if show_solution():
        from pprint import pprint

        for valid_cyclic_path in valid_cyclic_paths:
            figurates = {n: tuple((str(k) for k, v in p_numbers.items() if n in v)) for n in valid_cyclic_path}
            print(f"length={length!r} {figurates}")
            pprint(figurates)
    return [
        (len_paths := len(valid_cyclic_paths)),
        sum(valid_cyclic_paths[0]) if len_paths == 1 else [sum(path) for path in valid_cyclic_paths],
    ]


def main() -> int:
    setrecursionlimit(10**6)
    print(solve(length=int(argv[1])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
