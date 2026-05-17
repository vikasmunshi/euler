#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 56: Powerful Digit Sum [Level 1]. """
from __future__ import annotations

import sys
from sys import argv, stderr
from time import perf_counter
from typing import Any

import numpy as np


def visualize(
    data_matrix: np.ndarray[tuple[int, int], np.dtype[np.uint64]],
    len_matrix: np.ndarray[tuple[int, int], np.dtype[np.int_]],
    avg_matrix: np.ndarray[tuple[int, int], np.dtype[np.float64]],
    *,
    num_digits: int,
    stop_at: int,
    start_at: int,
) -> None:
    import matplotlib.pyplot as plt
    import matplotlib.ticker

    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 5))
    cmap = matplotlib.colormaps["YlOrRd"].copy()
    cmap.set_under(cmap(0.0))
    max_value = int(data_matrix.max())
    row_indices, col_indices = max_coords = np.where(data_matrix == max_value)
    len_value = len_matrix[row_indices[0], col_indices[0]]
    avg_value = avg_matrix[row_indices[0], col_indices[0]]
    base, exp = (max_coords[0][0] + start_at, max_coords[1][0] + start_at)
    cmap.set_over("black")
    plt.sca(ax1)
    cax1 = ax1.imshow(
        data_matrix,
        cmap=cmap,
        aspect="equal",
        origin="lower",
        extent=(start_at, stop_at, start_at, stop_at),
        vmin=0,
        vmax=max_value - 1,
    )
    colorbar1 = plt.colorbar(cax1, ax=ax1, label="Digital Sum")
    max_info = f"max_value={max_value!r} at base={int(base)}, exp={int(exp)}"
    ax1.set_title(f"Digital Sum for num_digits={num_digits!r}\n({max_info})")
    ax1.set_xlabel("Exponent")
    ax1.set_ylabel("Base")
    ax1.format_coord = lambda x, y: f"base={int(y)}, exponent={int(x)}"
    cax1.format_cursor_data = lambda data: f"digital sum={int(data)}"
    ax1.grid(visible=False, which="both")
    plt.sca(ax2)
    cax2 = ax2.imshow(
        len_matrix, cmap=cmap, aspect="equal", origin="lower", extent=(start_at, stop_at, start_at, stop_at)
    )
    colorbar2 = plt.colorbar(cax2, ax=ax2, label="Length Digits")
    max_info = f"value at base={int(base)}, exp={int(exp)} is {len_value:.0f} digits long"
    ax2.set_title(f"Length Digital Sum for num_digits={num_digits!r}\n({max_info})")
    ax2.set_xlabel("Exponent")
    ax2.set_ylabel("Base")
    ax2.format_coord = lambda x, y: f"base={int(y)}, exponent={int(x)}"
    cax2.format_cursor_data = lambda data: f"len digits={data}"
    ax2.grid(visible=False, which="both")
    plt.sca(ax3)
    cax3 = ax3.imshow(
        avg_matrix, cmap=cmap, aspect="equal", origin="lower", extent=(start_at, stop_at, start_at, stop_at)
    )
    colorbar3 = plt.colorbar(cax3, ax=ax3, label="Average Digit Value")
    max_info = f"value at base={int(base)}, exp={int(exp)} has {avg_value} average digit value"
    ax3.set_title(f"Average Digit Value for num_digits={num_digits!r}\n({max_info})")
    ax3.set_xlabel("Exponent")
    ax3.set_ylabel("Base")
    ax3.format_coord = lambda x, y: f"base={int(y)}, exponent={int(x)}"
    cax3.format_cursor_data = lambda data: f"avg digit={data:.1f}"
    ax3.grid(visible=False, which="both")
    for axis in (
        colorbar1.ax.xaxis,
        colorbar1.ax.yaxis,
        colorbar2.ax.xaxis,
        colorbar2.ax.yaxis,
        colorbar3.ax.xaxis,
        colorbar3.ax.yaxis,
    ):
        axis.set_major_locator(matplotlib.ticker.MaxNLocator(nbins="auto", integer=True, min_n_ticks=1, prune="both"))
        axis.set_major_formatter(matplotlib.ticker.FormatStrFormatter("%d"))
        axis.set_ticks_position("both")
    plt.tight_layout()
    plt.show()


def solve(*, num_digits: int) -> int:
    stop_at: int = 10**num_digits
    if sys.argv[-1] != "--show":
        return max(
            [
                sum([int(d) for d in str(base**exp)])
                for base in range(max(1, stop_at - 100), stop_at)
                for exp in range(max(1, stop_at - 10), stop_at)
            ]
        )
    else:
        data_matrix: np.ndarray[tuple[int, int], np.dtype[np.uint64]]
        start_at: int = max(1, stop_at - 100)
        data_matrix = np.zeros(shape=(stop_at - start_at, stop_at - start_at), dtype=np.uint64)
        for base, exp in ((base, exp) for base in range(start_at, stop_at) for exp in range(start_at, stop_at)):
            num = base**exp
            num_str = str(num)
            data_matrix[base - start_at, exp - start_at] = sum((int(d) for d in num_str))
        vectorized_len: np.vectorize = np.vectorize(lambda value: len(str(value)))
        len_matrix: np.ndarray[tuple[int, int], np.dtype[np.int_]] = vectorized_len(data_matrix)
        vectorized_avg: np.vectorize = np.vectorize(lambda value, length: sum([int(d) for d in str(value)]) / length)
        avg_matrix: np.ndarray[tuple[int, int], np.dtype[np.float64]] = vectorized_avg(data_matrix, len_matrix)
        print(data_matrix)
        print(f"data_matrix.shape={data_matrix.shape!r}")
        print(len_matrix)
        print(f"len_matrix.shape={len_matrix.shape!r}")
        print(avg_matrix)
        print(f"avg_matrix.shape={avg_matrix.shape!r}")
        print(f"avg_matrix.max()={avg_matrix.max()!r}")
        visualize(
            data_matrix=data_matrix,
            len_matrix=len_matrix,
            avg_matrix=avg_matrix,
            num_digits=num_digits,
            stop_at=stop_at,
            start_at=start_at,
        )
        return int(data_matrix.max())


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
    raise SystemExit(main(num_digits=int(argv[1])))
