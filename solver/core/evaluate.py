#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Solution evaluation: runs standalone scripts against test cases and reports results."""
from __future__ import annotations

from ast import literal_eval
from json import JSONDecodeError, loads
from pathlib import Path
from subprocess import TimeoutExpired, run
from time import perf_counter
from typing import Any, Literal

from solver.core.config import config
from solver.core.lock import check_workspace_lock
from solver.core.results import results_collector
from solver.core.console import console, register
from solver.utils.path_utils import canonical_path


@register(name='build',
          help='Build all C source files in the workspace directory.',
          usage='build', )
@check_workspace_lock
def build_c() -> None:
    """Build all C source files in the workspace directory."""
    source_files: list[Path] = sorted(s for s in config.workspace_dir.iterdir() if s.is_file() and s.suffix == '.c')
    for source_file in source_files:
        cmdline: str = f'{config.ScriptPaths.BUILD_C} {canonical_path(source_file)}'
        process = run(cmdline, capture_output=True, cwd=config.root_dir, shell=True, text=True)
        if process.returncode != 0:
            console.print(f'[error]error:[/error] building [accent]{source_file.name}[/accent]')
            output = process.stdout + ('\n' if process.stdout and process.stderr else '') + process.stderr
            if output.strip():
                console.print(output.strip(), markup=False, highlight=False)
        else:
            console.print(f'[success]built[/success] [accent]{source_file.name}[/accent] '
                          f'[muted]({process.stdout.strip()})[/muted]')


def eval_solution[T](filename: str, *,
                     disable_timeout: bool,
                     expected: T,
                     input_args: list[str],
                     runs: int,
                     show: bool,
                     work_dir: Path,
                     ) -> tuple[T | None, float, str]:
    """
    Run a solution script against a single set of input arguments and capture its result.

    The script is executed as a subprocess from work_dir. Its stdout is parsed into the
    same type as expected; complex types (list, tuple, dict) are parsed with ast.literal_eval,
    all others are cast via the expected type's constructor.

    Args:
        filename:           Name of the executable to run (relative to work_dir).
        disable_timeout:    If True, disables timeouts for script execution.
        expected:           The expected answer; its type determines how stdout is parsed.
                            Pass None to indicate an unknown answer (int parsing is assumed).
        input_args:         Command-line arguments passed to the script.
        runs:               The script's '--runs=' argument to specify the number of runs.
        show:               If True, the script is run with '--show' appended to the arguments.
        work_dir:           Directory from which the script is executed.

    Returns:
        A 3-tuple of (answer, average_elapsed_seconds, error_message).
        The answer is None on timeout or non-zero exit; error_message is empty on success.
    """
    expected_type: type = type(expected) if expected is not None else int
    timeout: float = config.timeout_single if runs == 1 else config.timeout_multiple * runs
    t_start: float = perf_counter()
    try:
        result = run([f'./{filename}', *input_args, f'--runs={runs}', '--show' if show else ''],
                     cwd=work_dir, capture_output=True, text=True, timeout=None if disable_timeout else timeout)
    except TimeoutExpired:
        return None, (perf_counter() - t_start) / runs, f'TimeoutExpired: {timeout}s'
    else:
        average: float = (perf_counter() - t_start) / runs
    try:
        assert result.returncode == 0, f'Non-zero exit code: {result.returncode}'
        output_lines: list[str] = result.stdout.splitlines()
        if len(output_lines) > 1:
            console.print('\n'.join(output_lines[:-1]), markup=False)
        _runs, _average, _answer = output_lines[-1].split(' ', maxsplit=2)
        assert runs == int(_runs), f'Expected {runs} runs, got {_runs}'
        average = float(_average)  # <= replace elapsed in eval_solution with _average reported by the called script
        answer: T = literal_eval(_answer) if expected_type in (list, tuple, dict) else expected_type(_answer)
    except (AssertionError, ValueError, SyntaxError) as e:
        return None, average, (f'Error in output\n{result.returncode=}\n{result.stdout=}\n{result.stderr=}\n'
                               f'({e.__class__.__name__}: {e})')
    return answer, average, ''


@register(name='evaluate',
          help='Evaluate solutions against test cases.',
          usage='evaluate [all|dev|main|extra ...] '
                '[disable_timeout=false] [lang=*|py|c] [record=false] [runs=1] [show=false] [solution=]',
          aliases=('eval', 'test'))
def evaluate(*categories: Literal['all', 'dev', 'main', 'extra'],
             disable_timeout: bool = False,
             lang: Literal['*', 'py', 'c'] = '*',
             record: bool = False,
             runs: int = 1,
             show: bool = False,
             solution: str | None = None,
             ) -> bool:
    """
    Run all solutions in workspace_dir against the filtered test cases and report results.

    Test cases are read from the workspace's test cases file and filtered to the given
    categories. Each solution (any executable file in workspace_dir) is run against every
    matching test case via eval_solution, and each result is passed to the result recorder.

    Args:
        *categories:        Test case categories to include. Accepts 'dev', 'main', 'extra', or 'all'
                            (which expands to all three). Defaults to ('dev', 'main') if omitted.
        disable_timeout:    If True, disables timeout for solution execution. Defaults to False.
        lang:               Language to evaluate. Accepts '*', 'py' or 'c'. Defaults to '*'.
        record:             If True, persists the evaluation results via the result recorder.
                            Defaults to False.
        runs:               Number of times to run each solution per test case (useful for timing).
                            Defaults to 1.
        show:               If True, appends '--show' to the arguments passed to each solution;
                            forces 'record' to False and 'runs' to 1. Defaults to False.
        solution:           Specific solution to evaluate.
                            If provided, only this solution will be evaluated.
                            If None, all solutions will be evaluated. Defaults to None.

    Returns:
                        True if evaluation is completed without errors
                        (solutions found, test cases found, no execution errors).
    """
    if not categories:
        categories = ('dev', 'main')
    if 'all' in categories:
        categories = ('dev', 'main', 'extra')
    if show:
        record = False
        runs = 1
    test_cases_path: Path = config.workspace_dir / config.test_cases_filename
    try:
        test_cases: list[dict[str, Any]] = loads(test_cases_path.read_text())
        assert test_cases and isinstance(test_cases, list), 'empty or invalid test cases file'
        filtered: list[dict[str, Any]] = [tc for tc in test_cases if tc['category'] in categories]
        assert filtered
    except FileNotFoundError:
        console.print('[error]error:[/error] no test cases found, skipping evaluation')
        return False
    except AssertionError:
        console.print(f'[error]error:[/error] no test cases for categories: {categories}, skipping evaluation')
        return False
    except JSONDecodeError as err:
        console.print(f'[error]error:[/error] invalid test cases file, skipping evaluation {err=}')
        return False
    if lang in ('*', 'c'):
        build_c()
    if solution is not None:
        solutions: list[str] = [solution]
    else:
        solutions = sorted((f'{s.name}' for s in config.workspace_dir.iterdir()
                            if s.is_file() and bool(s.stat().st_mode & 0o100)),
                           key=lambda name: (name.rsplit('.', 1)[-1] if '.' in name else '', name))
    if lang != '*':
        solutions = [s for s in solutions if s.endswith(lang)]
    if not solutions:
        console.print('[error]error:[/error] no solutions found, skipping evaluation')
        return False
    len_input_args_str: int = 0
    for test_case in filtered:
        input_args: list[str] = [str(v) for v in test_case['input'].values()]
        test_case['input_args'] = input_args
        input_args_str: str = ' '.join(input_args)
        test_case['input_args_str'] = input_args_str
        len_input_args_str = max(len_input_args_str, len(input_args_str))
    for test_case in filtered:
        test_case['input_args_str'] = f'{test_case["input_args_str"]:<{len_input_args_str}}'
    no_errors: bool = True
    with results_collector(record=record) as recorder:
        for test_case, solution in ((tc, s) for tc in filtered for s in solutions):
            expected: Any = test_case.get('answer')
            input_args = test_case['input_args']
            input_args_str = test_case['input_args_str']
            category: str = test_case['category']
            answer, elapsed, error = eval_solution(
                solution,
                disable_timeout=disable_timeout,
                expected=expected,
                input_args=input_args,
                runs=runs,
                show=show,
                work_dir=config.workspace_dir,
            )
            match (answer, expected, error):
                case (None, _, error_msg) if 'OverflowError:' in error_msg:
                    verdict = 'overflow'
                case (None, _, error_msg) if 'TimeoutExpired:' in error_msg:
                    verdict = 'timeout'
                case (None, _, _):
                    verdict = 'error'
                    no_errors = False
                case (_, None, _):
                    verdict = 'unknown'
                case (ans, exp, _) if ans == exp:
                    verdict = 'correct'
                case _:
                    verdict = 'incorrect'
            recorder(category=category, solution=solution, args=input_args_str, answer=answer, verdict=verdict,
                     elapsed=elapsed, runs=runs)
    return no_errors


__all__ = ('evaluate',)
