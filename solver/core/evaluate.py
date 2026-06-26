#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Solution evaluation: runs standalone scripts against test cases and reports results."""
from __future__ import annotations

__all__ = ['benchmark', 'evaluate']

import re
from ast import literal_eval
from pathlib import Path
from subprocess import TimeoutExpired, run
from time import perf_counter
from typing import Literal, cast

from solver.config import ExitCodes, config
from solver.core.results import results_collector
from solver.core.test_cases import TestCase, load_test_cases
from solver.shell import console, register, variables
from solver.utils.path_utils import canonical_path

# group 1: problem number, group 2: solution index, group 3: file type
_solution_file_prefix: re.Pattern[str] = re.compile(r'^p(\d{4})_s(\d+)(?:\.py|_c)$')


@register(help_text='Build all C source files in the solutions_dir.', quietable=True)
def compile_c(clean: bool = False) -> int:
    """Compile every C solution in the workspace into a runnable binary.

    Builds each `.c` file in `workspace/` (linking the runner harness) so it can
    be evaluated and benchmarked; reports per-file success or the compiler
    error. `eval --clean` and `benchmark` invoke this for you, so you rarely
    call it directly.

    Args:
        problem_number:     problem number to compile.
        clean:              When True, force a full rebuild instead of reusing up-to-date
                            build output. Defaults to False.
    """
    source_files: list[Path] = sorted(s for s in variables.problem.solution_dir.iterdir()
                                      if s.is_file() and s.suffix == '.c')
    result: int = ExitCodes.EXIT_OK
    for source_file in source_files:
        cmdline: str = f'{config.scripts.compile_c} {canonical_path(source_file)} {'--clean' if clean else ''}'
        process = run(cmdline, capture_output=True, cwd=config.root_dir, shell=True, text=True)
        if process.returncode != 0:
            console.print(f'[error]error:[/error] compiling [accent]{source_file.name}[/accent]')
            output = process.stdout + ('\n' if process.stdout and process.stderr else '') + process.stderr
            if output.strip():
                console.print(output.strip(), markup=False, highlight=False)
            result = ExitCodes.EXIT_ERROR
        else:
            console.print(f'[accent]{source_file.name}[/accent] '
                          f'[muted]{process.stdout.strip()}[/muted]')
    return result


def _eval_solution[T](filename: str, *,
                      timeout: float | None = None,
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
        timeout:            Timeout in seconds for script execution. If None, uses default.
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
    if disable_timeout:
        timeout = None
    else:
        timeout = timeout or (config.timeout_single if runs == 1 else (config.timeout_multiple * runs))
    t_start: float = perf_counter()
    try:
        result = run([f'./{filename}', *input_args, f'--runs={runs}', *(['--show'] if show else [])],
                     cwd=work_dir, capture_output=True, text=True, timeout=timeout)
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


def _evaluate(*categories: Literal['dev', 'main', 'extra'],
              clean: bool = False,
              timeout: float | None = None,
              disable_timeout: bool = False,
              lang: Literal['*', 'py', 'c'] = '*',
              record: bool = False,
              reset: bool = False,
              runs: int | None = None,
              show: bool = False,
              solution_index: int | None = None,
              verbose: bool = False,
              ) -> int:
    """
    Run all solutions in problem.solutions_dir against the filtered test cases and report results.

    Test cases are read from the workspace's test cases file and filtered to the given
    categories. Each solution (any executable file in problem.solutions_dir) is run against every
    matching test case via eval_solution, and each result is passed to the result recorder.

    Args:
        *categories:        Test case categories to include. Accepts 'dev', 'main', 'extra', or 'all'
                            (which expands to all three). Defaults to ('dev', 'main') if omitted.
        clean:              If True, force compiles C solutions. Defaults to False.
        timeout:            Timeout in seconds for solution execution. If None, uses default.
        disable_timeout:    If True, disables timeout for solution execution. Defaults to False.
        lang:               Language to evaluate. Accepts '*', 'py' or 'c'. Defaults to '*'.
        record:             If True, persists the evaluation results via the result recorder.
                            Defaults to False.
        reset:              If True (and "record" is True), replace any existing persisted results
                            with the new run on a clean completion. On an interrupted run the
                            existing results are preserved untouched — nothing is written, so a
                            partial reset cannot overwrite previously good data. Defaults to False.
        runs:               Number of times to run each solution per test case (useful for timing).
                            Defaults to 1.
        show:               If True, appends '--show' to the arguments passed to each solution;
                            forces 'record' to False and 'runs' to 1. Defaults to False.
        solution_index:     Specific solution index to evaluate.
                            If provided, only this solution index will be evaluated.
                            If None, all solutions will be evaluated. Defaults to None.
        verbose:            If True, prints error information during evaluation. Defaults to False.

    Returns:
                        True if evaluation is completed without errors
                        (solutions found, test cases found, no execution errors).
    """
    if not categories:
        categories = ('dev', 'main')
    if show:
        record = False
        runs = 1
    if disable_timeout:
        runs = 1
    if lang in ('*', 'c'):
        compile_c(clean=clean)
    solutions: list[str] = sorted(
        (
            f'{s.name}' for s in variables.problem.solution_dir.iterdir()
            if s.is_file()  # is a file
            if bool(s.stat().st_mode & 0o100)  # is executable
            if (match := _solution_file_prefix.match(s.name))  # matches pN_sK[.py|_c]
            if solution_index is None or match.group(2) == str(solution_index)  # matches solution_index
            if lang == '*' or s.name.endswith(lang)  # matches lang
        ),
        key=lambda name: (name.rsplit('.', 1)[-1] if '.' in name else '', name))
    if not solutions:
        console.print('[error]error:[/error] no solutions found, skipping evaluation')
        return ExitCodes.EXIT_ERROR
    test_cases: list[TestCase] = load_test_cases(*categories, solutions=solutions, runs=runs)
    if not test_cases:
        return ExitCodes.EXIT_ERROR
    rc: int = ExitCodes.EXIT_OK
    with results_collector(record=record, reset=reset) as recorder:
        for test_case, solution in ((tc, s) for tc in test_cases for s in solutions):
            answer, elapsed, error = _eval_solution(solution,
                                                    timeout=timeout,
                                                    disable_timeout=disable_timeout,
                                                    expected=test_case.answer,
                                                    input_args=test_case.input_args,
                                                    runs=test_case.runs,
                                                    show=show,
                                                    work_dir=variables.problem.solution_dir, )
            match (answer, test_case.answer, error):
                case (None, _, error_msg) if 'ModuleNotFoundError:' in error_msg:
                    verdict = 'missing dep'
                case (None, _, error_msg) if 'OverflowError:' in error_msg:
                    verdict = 'overflow'
                case (None, _, error_msg) if 'TimeoutExpired:' in error_msg:
                    verdict = 'timeout'
                case (None, _, error_msg) if 'implement solve() first' in error_msg:
                    verdict = 'no solve'
                case (None, _, _):
                    verdict = 'error'
                    rc = ExitCodes.EXIT_ERROR
                case (_, None, _):
                    verdict = 'unknown'
                case (ans, exp, _) if ans == exp:
                    verdict = 'correct'
                case _:
                    verdict = 'incorrect'
                    rc = ExitCodes.EXIT_ERROR
            if verbose and verdict not in ('correct', 'incorrect', 'unknown'):
                console.print(f'[error]error:[/error] {verdict} for {solution} on {test_case.category}\n'
                              f'[error]{error}[/error]')
            recorder(category=test_case.category,
                     solution=solution,
                     args=test_case.input_args_str,
                     answer=answer,
                     verdict=verdict,
                     elapsed=elapsed,
                     runs=test_case.runs, )
    return rc


@register(help_text='Evaluate solutions against test cases.', aliases=('eval',), quietable=True)
def evaluate(*categories: Literal['all', 'dev', 'main', 'extra'],
             clean: bool = False,
             timeout: float | None = None,
             disable_timeout: bool = False,
             lang: Literal['*', 'py', 'c'] = '*',
             runs: int = 1,
             show: bool = False,
             solution_index: int | None = None,
             verbose: bool = False,
             ) -> int:
    """
    Evaluate solutions against test cases.

    Args:
    *categories:        Test case categories to include. Accepts 'dev', 'main', 'extra', or 'all'
                        (which expands to all three). Defaults to 'dev', 'main' if omitted.
    clean:              If True, force compiles C solutions. Defaults to False.
    timeout:            Timeout in seconds for solution execution. If None, uses default timeout.
                        Defaults to None.
    disable_timeout:    If True, disables timeout for solution execution. Defaults to False.
                        If True, only one run will be performed for each solution.
    lang:               Language to evaluate. Accepts '*', 'py' or 'c'. Defaults to '*'.
    runs:               Number of times to run each solution per test case (useful for timing).
                        Defaults to 1.
    show:               If True, appends '--show' to the arguments passed to each solution;
                        defaults to False.
    solution_index:     Specific solution index to evaluate.
                        If provided, only this solution index will be evaluated.
                        If None, all solutions will be evaluated. Defaults to None.
    verbose:            If True, prints error information during evaluation. Defaults to False.
    """
    if not categories:
        eval_categories: list[Literal['dev', 'main', 'extra']] = ['dev', 'main']
    elif 'all' in categories:
        eval_categories = ['dev', 'main', 'extra']
    else:
        eval_categories = cast(list[Literal['dev', 'main', 'extra']], list(categories))
    try:
        rc: int = _evaluate(*eval_categories,
                            clean=clean,
                            timeout=timeout,
                            disable_timeout=disable_timeout,
                            lang=lang,
                            runs=runs,
                            show=show,
                            solution_index=solution_index,
                            verbose=verbose, )
    except KeyboardInterrupt:
        console.print('[muted]Evaluate interrupted by user.[/muted]')
        return ExitCodes.EXIT_ERROR
    return rc


@register(help_text='Benchmark the problem currently in the workspace.', quietable=True)
def benchmark(*categories: Literal['all', 'dev', 'main', 'extra'],
              clean: bool = False,
              timeout: float | None = None,
              disable_timeout: bool = False,
              lang: Literal['*', 'py', 'c'] = '*',
              solution_index: int | None = None,
              reset: bool = False,
              verbose: bool = False,
              ) -> int:
    """Measure and record the execution time of the workspace solutions.

    Like `eval`, runs every solution against the chosen test-case categories, but
    always **records** the timings to `results.json` and repeats each case an
    adaptive number of times (see "Repeats") instead of running once. Run `eval`
    first to confirm correctness, then `benchmark` to measure; categories default
    to all three ('dev', 'main', 'extra').

    Repeats:
        `benchmark` does not take a `runs` argument — it passes `runs=None` to the
        evaluator, which makes `load_test_cases` (`core/test_cases.py`) choose the
        repeat count **per test-case category** from the previously recorded
        timings::

            runs = clamp(round(21 / slowest_prior_average), 1, 21)

        where `slowest_prior_average` is the largest recorded average (seconds per
        run) among prior *correct* results for that category and the solutions
        being benchmarked. So each case is repeated ~21 times when it runs in well
        under a second and scales down toward a single run as it gets slower —
        keeping the per-category wall time bounded at roughly 21s — clamped to the
        1..21 range. With no prior correct result recorded for a category the
        count is 1: the first benchmark establishes a one-run baseline, and later
        benchmarks use it to repeat the fast cases and average out noise. Passing
        `disable_timeout` overrides this and forces a single run.

    Args:
        *categories:        Test case categories to include. Accepts 'dev', 'main', 'extra', or 'all'
                            (which expands to all three). Defaults to all three if omitted.
        clean:              If True, force compiles C solutions. Defaults to False.
        timeout:            Per-run timeout in seconds for solution execution. If None, uses the
                            default timeout. Defaults to None.
        disable_timeout:    If True, disables the timeout for solution execution and forces a single
                            run (bypassing the adaptive repeat count above). Defaults to False.
        lang:               Language to evaluate. Accepts '*', 'py' or 'c'. Defaults to '*'.
        solution_index:     Specific solution index to evaluate.
                            If provided, only this solution index will be evaluated.
                            If None, all solutions will be evaluated. Defaults to None.
        reset:              If True, replace any existing persisted results with this run on a
                            clean completion. If the benchmark is interrupted, existing results
                            are preserved untouched. Defaults to False (results are merged with
                            existing records as a running average).
        verbose:            If True, prints error information during evaluation. Defaults to False.
    """
    if not categories or 'all' in categories:
        eval_categories: list[Literal['dev', 'main', 'extra']] = ['dev', 'main', 'extra']
    else:
        eval_categories = cast(list[Literal['dev', 'main', 'extra']], list(categories))
    try:
        rc: int = _evaluate(*eval_categories,
                            clean=clean,
                            timeout=timeout,
                            disable_timeout=disable_timeout,
                            lang=lang,
                            record=True,
                            reset=reset,
                            runs=None,
                            show=False,
                            solution_index=solution_index,
                            verbose=verbose, )
    except KeyboardInterrupt:
        console.print('[muted]Benchmark interrupted by user.[/muted]')
        return ExitCodes.EXIT_ERROR
    return rc
