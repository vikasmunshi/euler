#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Solution evaluation: runs standalone scripts against test cases and reports results."""
from __future__ import annotations

from ast import literal_eval
from functools import partial
from json import JSONDecodeError, dumps, loads
from pathlib import Path
from subprocess import TimeoutExpired, run
from time import perf_counter
from typing import Any, Literal

from solver.config import ColorCodes, results_filename, root_dir, test_cases_filename, timeout

RESET = ColorCodes.RESET


def eval_solution[T](filename: str, input_args: list[str], work_dir: Path, expected: T) -> tuple[T | None, float, str]:
    """
    Run a solution script against a single set of input arguments and capture its result.

    The script is executed as a subprocess from work_dir. Its stdout is parsed into the
    same type as expected; complex types (list, tuple, dict) are parsed with ast.literal_eval,
    all others are cast via the expected type's constructor.

    Args:
        filename:   Name of the executable script to run (relative to work_dir).
        input_args: Command-line arguments passed to the script.
        work_dir:   Directory from which the script is executed.
        expected:   The expected answer; its type determines how stdout is parsed.
                    Pass None to indicate an unknown answer (int parsing is assumed).

    Returns:
        A 3-tuple of (answer, elapsed_seconds, error_message).
        The answer is None on timeout or non-zero exit; error_message is empty on success.
    """
    expected_type: type = type(expected) if expected is not None else int
    t_start: float = perf_counter()
    try:
        result = run([f'./{filename}'] + input_args, cwd=work_dir, capture_output=True, text=True, timeout=timeout)
    except TimeoutExpired:
        return None, perf_counter() - t_start, f'Timed out after {timeout}s'
    elapsed: float = perf_counter() - t_start
    if result.returncode != 0:
        return None, elapsed, result.stderr
    raw: str = result.stdout.strip()
    try:
        answer: T = literal_eval(raw) if expected_type in (list, tuple, dict) else expected_type(raw)
    except (ValueError, SyntaxError) as e:
        return None, elapsed, f'Error {e.__class__.__name__}: {e}'
    finally:
        raw_stderr: str = result.stderr.strip()
        if raw_stderr:
            print(raw_stderr)
    return answer, elapsed, ''


def as_input_args(test_case: dict[str, Any]) -> list[str]:
    """Convert a test case's input dict to a flat list of string arguments."""
    return [str(v) for v in test_case['input'].values()]


def evaluate(*categories: Literal['all', 'dev', 'main', 'extra'],
             workspace_dir: Path,
             show: bool = False,
             record: bool = False) -> bool:
    """
    Evaluates solutions against the provided test cases by filtering test cases based on specified categories and
    executing each solution with test case inputs. Results of the evaluation can be displayed, and outputs can be saved.

    Args:
    workspace_dir: Path to the workspace directory.
    *categories (Literal['all', 'dev', 'main', 'extra']):
        Categories of test cases to include, defaults to ('dev', 'main') if no categories are provided.
    show (bool):
        If True, adds --show at the end of the cmd-line arguments used while evaluating the solution. Defaults to False.
    record (bool):
        If True, saves the evaluation results to the result.txt file. Defaults to False.

    Returns:
    bool:
        True if the evaluation is successful, i.e., at least one test case is found for the categories,
        solutions are present, and no critical errors occur during execution.
    """
    if not categories:
        categories = ('dev', 'main')
    if 'all' in categories:
        categories = ('dev', 'main', 'extra')
    test_cases_path: Path = workspace_dir / test_cases_filename
    try:
        test_cases: list[dict[str, Any]] = loads(test_cases_path.read_text())
        assert test_cases and isinstance(test_cases, list), 'empty or invalid test cases file'
        filtered: list[dict[str, Any]] = [tc for tc in test_cases if tc['category'] in categories]
        assert filtered
    except FileNotFoundError:
        print('Error: no test cases found, skipping evaluation')
        return False
    except AssertionError:
        print(f'Error: no test cases for categories: {categories}, skipping evaluation')
        return False
    except JSONDecodeError as err:
        print(f'Error: invalid test cases file, skipping evaluation {err=}')
        return False
    solutions: list[str] = sorted(f'{s.name}' for s in workspace_dir.iterdir()
                                  if s.is_file() and bool(s.stat().st_mode & 0o100))
    if not solutions:
        print('Error: no solutions found, skipping evaluation')
        return False
    no_errors: bool = True
    output: list[dict[str, Any]] = []

    def collect_output(*,
                       category: str,
                       args: str,
                       solution: str,
                       answer: str,
                       verdict: str,
                       elapsed: float,
                       color: ColorCodes,
                       error: str = '',
                       ) -> None:
        print(f'{color}{category} {solution} {args} -> {answer} ({verdict}) [{elapsed:.3f}s] {error}{RESET}')
        if record:
            output.append({'category': category, 'solution': solution, 'args': args, 'answer': answer,
                           'verdict': verdict, 'elapsed': elapsed})

    for test_case in filtered:
        expected: Any = test_case.get('answer')
        input_args: list[str] = as_input_args(test_case)
        if show:
            input_args.append('--show')
        collect_partial = partial(collect_output, category=test_case['category'], args=' '.join(input_args))
        for _solution in solutions:
            collect = partial(collect_partial, solution=_solution)
            _answer, _elapsed, _error = eval_solution(_solution, input_args, workspace_dir, expected)
            if _answer is None:
                if 'OverflowError:' in _error:
                    collect(answer='', verdict='Overflow', elapsed=_elapsed, color=ColorCodes.RED)
                elif 'Timed out' in _error:
                    collect(answer='', verdict='Timeout', elapsed=_elapsed, color=ColorCodes.RED)
                else:
                    collect(answer='', verdict='Error', elapsed=_elapsed, color=ColorCodes.RED, error=_error)
                    no_errors = False
            elif expected is None:
                collect(answer=_answer, verdict='Unknown', elapsed=_elapsed, color=ColorCodes.BLUE)
            elif _answer == expected:
                collect(answer=_answer, verdict='Correct', elapsed=_elapsed, color=ColorCodes.GREEN)
            else:
                collect(answer=_answer, verdict='Wrong', elapsed=_elapsed, color=ColorCodes.RED)
    if record:
        (results_file := workspace_dir / results_filename).write_text(dumps(output, indent=None))
        print(f'Results saved to {results_file.relative_to(root_dir).as_posix()}')
    return no_errors


__all__ = ('evaluate',)
