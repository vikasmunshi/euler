#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Generate and re-document Project Euler solutions (Python and C) via the Claude API.

Three public commands drive a model to emit solution files in `// BEGIN <file> ... // END <file>`
blocks, then validate each generated file - compile (C), run every answered test case, and lint -
retrying with the failures fed back until the files pass or the retry budget is exhausted.
"""
from __future__ import annotations

__all__ = ['document_code', 'generate_c_code', 'generate_py_code']

from ast import literal_eval
from functools import partial
from json import loads
from pathlib import Path
from re import DOTALL, MULTILINE, compile as re_compile
from subprocess import TimeoutExpired, run
from time import time
from typing import Any, Callable, Literal, NamedTuple, Protocol, runtime_checkable

from anthropic import APIError
from anthropic.types import MessageParam

from solver.ai.facts import Facts, format_solutions_markdown, gather_facts, prepare_anthropic_request
from solver.ai.models import Model, record_usage
from solver.config import config
from solver.core.problems import Problem, problems
from solver.shell import console
from solver.templates.engine import Templates, filled_template, get_template
from solver.utils.path_utils import canonical_path, iterdir_recursive, write_file

# ----------------------------------------------------------------------------------------------------
# Response parsing
# ----------------------------------------------------------------------------------------------------

_FENCE = re_compile(r'^[ \t]*(?:`{3,}|~{3,})[^\n]*\n(?P<body>.*)\n[ \t]*(?:`{3,}|~{3,})[ \t]*$', DOTALL)
_PATTERN = re_compile(r'^// BEGIN (\S+)\n(.*?)\n// END \1', MULTILINE | DOTALL)


def _strip_code_fence(code: str) -> str:
    """Drop a surrounding markdown code fence the model sometimes emits inside the delimiters.

    The // BEGIN / // END block should contain raw source, but a stray ```c ... ``` (or ~~~) wrapper
    leaks backticks into the file and breaks compilation. If the trimmed code both opens and closes
    with a fence line, return the body between them; otherwise return the code unchanged.
    """
    stripped: str = code.strip('\n')
    match = _FENCE.match(stripped)
    fixed = match.group('body') if match else code
    return fixed + '\n'


def _retry_missing_message(truncated: bool, files_to_generate: str) -> str:
    """Build the retry-prompt user message when the previous response had no parseable solutions."""
    if truncated:
        reason = 'Your previous response was truncated before any complete solution block was emitted.'
    else:
        reason = 'Your previous response did not contain any valid solution blocks.'
    return (f'{reason} '
            f'Please output all required solutions using the // BEGIN / // END format, '
            f'ensuring each block is fully closed.\n\n'
            f'Files to generate: {files_to_generate}')


class Solution(NamedTuple):
    name: str
    code: str
    file: Path
    executable: Path

    @staticmethod
    def from_msg(msg: str, problem: Problem) -> list[Solution]:
        """Parse solutions from an AI response containing // BEGIN / // END delimiters."""
        solutions: list[Solution] = []
        for m in _PATTERN.finditer(msg):
            name: str = m.group(1)
            code: str = _strip_code_fence(m.group(2))
            file: Path = problem.solution_dir / name
            suffix: str = file.suffix
            if suffix in ('.c', '.py'):
                write_file(file, code.encode(), f'generated {name}')
            if suffix == '.c':
                executable: Path = problem.solution_dir / f'{file.stem}_c'
            elif suffix == '.py':
                file.chmod(0o755)
                executable = file
            else:
                executable = file.with_suffix('.exe')
            solutions.append(Solution(name=name, code=code, file=file, executable=executable))
        return solutions


# ----------------------------------------------------------------------------------------------------
# Validation result types
# ----------------------------------------------------------------------------------------------------


class SolutionsCheckResults(NamedTuple):
    verdict: bool
    msg: str
    passed: list[str]
    failed: list[str]
    errors: dict[str, str]

    def as_msg(self) -> str:  # TO:DO, modify if required
        """Render the check results (verdict, message, passed/failed lists, errors) as Markdown."""
        if self.errors:
            errors_section = '## errors:\n\n'
            for filename, error in self.errors.items():
                errors_section += f'### errors in filename: {filename}\n\n{error}\n\n'
        else:
            errors_section = '## errors:\n\n(none)\n\n'
        return (
            f'## verdict:\n\n{'passed' if self.verdict else 'failed'}\n\n'
            f'## messages:\n\n{self.msg}\n\n'
            f'## passed:\n\n{"\n".join(f"- {s}" for s in self.passed) if self.passed else "(none)"}\n\n'
            f'## failed:\n\n{"\n".join(f"- {s}" for s in self.failed) if self.failed else "(none)"}\n\n'
            f'{errors_section}'
        )


@runtime_checkable
class Validator(Protocol):
    """Protocol for validator callables that check generated code."""

    def __call__(self, *,
                 attempt: int,
                 solutions: list[Solution],
                 ) -> SolutionsCheckResults:
        """
        Check the supplied solutions and return a verification result.

        Args:
            attempt:    The current attempt number for solution verification.
            solutions:  A list of Solution objects to be verified.

        Returns:
            A SolutionsCheckResults object containing the result of the verification process.
        """
        ...


# ----------------------------------------------------------------------------------------------------
# Generation driver
# ----------------------------------------------------------------------------------------------------


def _generate_code(
        model: Model,
        problem: Problem,
        label: Literal['c code', 'py code', 'doc'],
        prompt: str,
        retry_missing: Callable[[bool], str],
        validator: Validator,
        images: dict[str, bytes] | None = None,
) -> bool | None:
    """
    Drive a model to generate solutions, retrying on parse or validation failure.

    Args:
        model:          The language model used for generating solutions.
        label:          The label for the problem being solved.
        problem:        The problem for which solutions are being generated.
        prompt:         Template prompt to guide the model's solution generation.
        retry_missing:  Function to generate a retry message for missing solutions
                        differentiated based on if stop_reason was max_tokens.
        validator:      Callable used for validating generated solutions.
        images:         Optional map of resource filename to image bytes referenced in the
                        problem content; each is attached to the initial user message as an
                        image content block so the model can actually see the image.

    Returns:
        bool: True if solutions were successfully generated and validated,
        False on generation or validation failure after all retries.
    """

    try:
        client, system_blocks, messages = prepare_anthropic_request(prompt, images)
    except (ValueError, OSError) as e:
        console.print(f'[error]error:[/error] {type(e).__name__} preparing request for '
                      f'[accent]problem {problem.number}[/accent]: {e}')
        return False
    for attempt in range(1, config.max_retries + 1):
        console.print(f'[primary]Generating {label} for [accent]problem {problem.number}[/accent] '
                      f'(attempt {attempt}/{config.max_retries})...[/primary]')
        try:
            with client.messages.stream(model=model,
                                        max_tokens=config.max_output_tokens,
                                        system=system_blocks,
                                        messages=messages,
                                        timeout=config.api_timeout) as stream:
                response = stream.get_final_message()
        except APIError as e:
            console.print(f'[error]error:[/error] Anthropic API error for '
                          f'[accent]problem {problem.number}[/accent]: {e}')
            return False
        record_usage(model, response.usage)
        usage = response.usage
        console.print(f'[muted]Tokens used for [accent]problem {problem.number}[/accent]: '
                      f'input {usage.input_tokens}, output {usage.output_tokens}, '
                      f'cache_write {getattr(usage, "cache_creation_input_tokens", 0) or 0}, '
                      f'cache_read {getattr(usage, "cache_read_input_tokens", 0) or 0}, '
                      f'stop_reason {response.stop_reason!r}[/muted]')
        truncated: bool = response.stop_reason == 'max_tokens'
        if truncated:
            console.print(f'[warning]Warning: max_tokens reached for problem {problem.number}; '
                          f'response may be truncated[/warning]')
        text: str | None = next((b.text for b in response.content if b.type == 'text'), None)
        if text is None:
            console.print(f'[error]error:[/error] no text block in response for '
                          f'[accent]problem {problem.number}[/accent]')
            return False
        solutions: list[Solution] = Solution.from_msg(text, problem)
        if not solutions:
            console.print(f'[error]error:[/error] could not parse any solutions from response for '
                          f'[accent]problem {problem.number}[/accent]')
            if attempt < config.max_retries:
                retry_msg = retry_missing(truncated)
                messages.append(MessageParam(role='assistant', content=text))
                messages.append(MessageParam(role='user', content=retry_msg, ))
            continue
        result = validator(attempt=attempt, solutions=solutions)
        if result.verdict:
            return True
        if attempt < config.max_retries:
            messages.append(MessageParam(role='assistant', content=text))
            messages.append(MessageParam(
                role='user',
                content=(f'The following solutions failed validation:\n'
                         f'{','.join(result.failed)}\n\n'
                         f'Please fix only the failed solutions '
                         f'and return them in the same // BEGIN / // END format.\n\n'
                         f'{result.as_msg()}'),
            ))
    console.print(f'[error]error:[/error] failed to generate valid solutions for '
                  f'[accent]problem {problem.number}[/accent] '
                  f'after {config.max_retries} attempts')
    return False


# ----------------------------------------------------------------------------------------------------
# Validation: per-solution checks
# ----------------------------------------------------------------------------------------------------


def _check_solution_against_test_cases(*,
                                       solution: Solution,
                                       test_cases: list[dict[str, Any]],
                                       failed: set[str],
                                       errors: dict[str, str],
                                       expected_type: type,
                                       ) -> None:
    """Run *solution* against each test case, recording failures and errors in place.

    Executes the solution once per test case, parsing its final stdout line into
    *expected_type* and comparing it to the case's answer. A `dev`/`main` case that
    times out, exits non-zero (other than an OverflowError), or returns the wrong
    answer adds the solution to *failed*; the diagnostic text is collected in
    *errors* keyed by solution name. A `main` case with no recorded answer prompts
    the user to confirm the computed result interactively.
    """
    timeout = config.timeout_single
    for test_case in test_cases:
        category: str = test_case['category']
        input_args: list[str] = [str(v) for v in test_case['input'].values()]
        expected: Any | None = test_case['answer']
        cmdline = [f'{solution.executable}', *input_args, '--runs=1']
        try:
            process = run(
                cmdline,
                capture_output=True,
                text=True,
                cwd=config.root_dir,
                timeout=timeout,
            )
        except TimeoutExpired as e:
            console.print(f'cmdline: {" ".join(cmdline)}\nrc: -1\nstdout:\nstderr:\nerror: {e}\n',
                          markup=False, highlight=False)
            errors[solution.name] = (f'#### cmdline:\n\n{' '.join(cmdline)}\n\n'
                                     f'#### error:\n\ncmd did not complete within timeout of '
                                     f'{timeout} seconds\n\n'
                                     f'#### stdout:\n\n{(e.stdout or b'').decode()}\n\n'
                                     f'#### stderr:\n\n{(e.stderr or b'').decode()}\n\n')
            if test_case['category'] in ('dev', 'main'):
                failed.add(solution.name)
            continue
        else:
            console.print(f'cmdline: {" ".join(cmdline)}\nrc: {process.returncode}\n'
                          f'stdout: {process.stdout.strip('\n')}\nstderr: {process.stderr.strip('\n')}\n',
                          markup=False, highlight=False)
        if process.returncode != 0:
            if 'OverflowError:' not in (process.stderr or ''):
                failed.add(solution.name)
            errors[solution.name] = (f'#### cmdline:\n\n{' '.join(cmdline)}\n\n'
                                     f'#### error:\n\nprocess returned non-zero exit code {process.returncode}\n\n'
                                     f'#### stdout:\n\n{process.stdout}\n\n'
                                     f'#### stderr:\n\n{process.stderr}\n\n')
            break
        try:
            _runs, _average, _answer = process.stdout.splitlines()[-1].split(' ', maxsplit=2)
            answer = literal_eval(_answer) if expected_type in (list, tuple, dict) else expected_type(_answer)
            if category == 'main' and expected is None:
                console.print(f'[accent]{solution.name} {input_args} -> [bold]{_answer}[/bold][/accent]')
                assert console.input('is this correct? (y/n) ')[0].lower() == 'y', f'answer {_answer} is incorrect.'
            if expected is not None:
                assert answer == expected, f'incorrect answer {_answer}, expected {expected}'
        except (AssertionError, IndexError, ValueError) as err:
            failed.add(solution.name)
            existing_error = errors.get(solution.name, '')
            existing_error = existing_error + ('\n\n' if existing_error else '')
            errors[solution.name] = existing_error + (f'#### cmdline:\n\n{' '.join(cmdline)}\n\n'
                                                      f'#### error:\n\n{err}\n\n'
                                                      f'#### stdout:\n\n{process.stdout}\n\n'
                                                      f'#### stderr:\n\n{process.stderr}\n\n')


def _check_results(*,
                   passed: set[str],
                   failed: set[str],
                   errors: dict[str, str],
                   ) -> SolutionsCheckResults:
    """Aggregate the passed/failed sets and errors into a `SolutionsCheckResults` verdict."""
    if failed:
        verdict: bool = False
        msg: str = f'{len(failed)} solutions failed, {len(passed)} passed'
    else:
        verdict = True
        msg = f'{len(passed)} solutions passed'
    return SolutionsCheckResults(
        verdict=verdict,
        msg=msg,
        passed=sorted(passed),
        failed=sorted(failed),
        errors=dict(errors),
    )


def _check_c_solution(*,
                      solution: Solution,
                      test_cases: list[dict[str, Any]],
                      expected_type: type,
                      failed: set[str],
                      errors: dict[str, str],
                      ) -> None:
    """Compile and test one generated C solution, updating passed/failed/errors in place."""
    cmdline: list[str] = [config.scripts.compile_c, canonical_path(solution.file), '--clean']
    process = run(cmdline, capture_output=True, text=True, cwd=config.root_dir)
    console.print(f'cmdline: {" ".join(cmdline)}\nrc: {process.returncode}\n'
                  f'stdout:\n{process.stdout}\nstderr:\n{process.stderr}\n',
                  markup=False, highlight=False)
    if process.returncode != 0:
        failed.add(solution.name)
        errors[solution.name] = (f'#### cmdline:\n\n{' '.join(cmdline)}\n\n'
                                 f'#### error:\n\ncompilation failed\n\n'
                                 f'#### stdout:\n\n{process.stdout}\n\n'
                                 f'#### stderr:\n\n{process.stderr}\n\n')
        return
    _check_solution_against_test_cases(
        solution=solution,
        test_cases=test_cases,
        failed=failed,
        errors=errors,
        expected_type=expected_type,
    )


def _check_py_solution(*,
                       solution: Solution,
                       test_cases: list[dict[str, Any]],
                       expected_type: type,
                       failed: set[str],
                       errors: dict[str, str],
                       ) -> None:
    """Write and test one generated Python solution, updating passed/failed/errors in place."""
    # Validate the first two header lines exactly as the prompt and `new.py` template mandate:
    # line 1 is the python3.14 shebang, line 2 is the UTF-8 coding declaration.
    expected_header: tuple[str, str] = ('#!/usr/bin/env python3.14', '# -*- coding: utf-8 -*-')
    header_lines: list[str] = solution.code.split('\n', 2)[:2]
    actual_header: tuple[str, ...] = tuple(line.rstrip() for line in header_lines)
    if actual_header != expected_header:
        failed.add(solution.name)
        errors[solution.name] = (f'{solution.name} does not have the required header. '
                                 f'Expected first two lines to be {list(expected_header)!r}, '
                                 f'got {list(actual_header)!r}')
        return
    _check_solution_against_test_cases(
        solution=solution,
        test_cases=test_cases,
        failed=failed,
        errors=errors,
        expected_type=expected_type,
    )


def _lint_generated_code(*,
                         solution: Solution,
                         failed: set[str],
                         errors: dict[str, str],
                         ) -> None:
    """Lint one generated Python solution with flake8 and mypy, updating failed/errors in place.

    Functional validity (compile / run / answer) is checked elsewhere; this guards the static gates the
    committed solutions must pass (`flake8 --max-line-length 120` and `mypy`). A lint-only failure the
    model cannot reliably avoid by instruction alone - an over-long docstring line (E501), a missing
    trailing newline (W292), or a type error - is caught here and fed back into the retry loop instead
    of surfacing later at `lint` / `stack`. Both linters always run - even for a solution that already
    failed a functional check - so a single retry carries the functional and static fixes together,
    avoiding an extra pass. Only `.py` files are linted (neither tool has a C equivalent; C is covered
    by compilation).
    """
    if solution.file.suffix != '.py':
        return
    path: str = canonical_path(solution.file)

    def run_linter(cmdline: list[str], summary: str) -> None:
        process = run(cmdline, capture_output=True, text=True, cwd=config.root_dir)
        console.print(f'cmdline: {" ".join(cmdline)}\nrc: {process.returncode}\n'
                      f'stdout: {process.stdout.strip('\n')}\nstderr: {process.stderr.strip('\n')}\n',
                      markup=False, highlight=False)
        if process.returncode != 0:
            failed.add(solution.name)
            existing_error = errors.get(solution.name, '')
            existing_error = existing_error + ('\n\n' if existing_error else '')
            errors[solution.name] = existing_error + (
                f'#### cmdline:\n\n{' '.join(cmdline)}\n\n'
                f'#### error:\n\n{summary}\n\n'
                f'#### stdout:\n\n{process.stdout}\n\n'
                f'#### stderr:\n\n{process.stderr}\n\n')

    run_linter(['flake8', f'--max-line-length={config.max_line_length}', path],
               f'flake8 reported style violations; every line must pass '
               f'flake8 --max-line-length {config.max_line_length}')
    run_linter(['mypy', path],
               'mypy reported type errors; the solution must pass mypy with no errors')


def _check_generated_code(*,
                          problem: Problem,
                          attempt: int,
                          solutions: list[Solution],
                          test_cases: list[dict[str, Any]],
                          ) -> SolutionsCheckResults:
    """Check that generated solutions are functionally valid, dispatching per file by extension.

    Each solution is routed by its filename suffix: `.c` is compiled then run, `.py` is header-checked
    then run; any other extension fails immediately. Every functionally valid file is then linted
    (`.py` with flake8 and mypy) so a static-check-only violation is rejected and retried rather than
    surfacing later at `lint` / `stack`. A failed file is preserved as a `.bak` and removed. This
    single validator backs Python generation, C generation, and the documentation pass (which re-emits
    a mix of `.py` and `.c` files).
    """
    if not solutions:
        return SolutionsCheckResults(verdict=False, msg='No solutions found', passed=[], failed=[], errors={})
    passed: set[str] = set()
    failed: set[str] = set()
    errors: dict[str, str] = {}
    expected_type: type = next((type(tc['answer']) for tc in test_cases if tc['answer'] is not None), str)
    for solution in solutions:
        suffix: str = Path(solution.name).suffix
        if suffix == '.c':
            _check_c_solution(solution=solution, test_cases=test_cases, expected_type=expected_type,
                              failed=failed, errors=errors)
        elif suffix == '.py':
            _check_py_solution(solution=solution, test_cases=test_cases, expected_type=expected_type,
                               failed=failed, errors=errors)
        else:
            failed.add(solution.name)
            errors[solution.name] = f'{solution.name} is not a valid source filename, should end with .py or .c'
        _lint_generated_code(solution=solution, failed=failed, errors=errors)
        if solution.name in failed:
            # Preserve the rejected source as a .bak for debugging and drop it from the workspace so a
            # final-failure leftover is never stacked; a retry re-emits and rewrites it via from_msg.
            backup_file: Path = solution.file.with_suffix(f'.{attempt}{suffix}.bak')
            write_file(backup_file, solution.code.encode(), f'backup of failed {solution.name}')
            solution.file.unlink(missing_ok=True)
        else:
            passed.add(solution.name)
    final: SolutionsCheckResults = _check_results(passed=passed, failed=failed, errors=errors)
    if final.verdict:
        # success on any attempt: drop accumulated .bak litter from earlier retries
        for file in iterdir_recursive(problem.solution_dir, rt='path'):
            if file.suffix == '.bak':
                file.unlink(missing_ok=True)
    elif attempt == config.max_retries:
        # final attempt still failing: preserve the rejected sources
        backup_dir: Path = config.backup_dir / f'p{problem.number:04d}_{int(time())}'
        backup_dir.mkdir(parents=True, exist_ok=True)
        for file in iterdir_recursive(problem.solution_dir, rt='path'):
            if file.suffix == '.bak':
                file.rename(backup_dir / file.with_suffix('').name)
        console.print(f'[accent.dim]backup of failed solutions to {canonical_path(backup_dir)}[/accent.dim]')
    return final


# ----------------------------------------------------------------------------------------------------
# Public commands
# ----------------------------------------------------------------------------------------------------


def _load_test_cases(problem: Problem, filter_null_answers: bool) -> list[dict[str, Any]]:
    """Load *problem*'s test cases, optionally dropping those without an answer.

    Warns (or errors, when *filter_null_answers* is True) if no answered case is
    found, and reports when the answered cases mix more than one answer type.
    """
    test_cases: list[dict[str, Any]] = loads((problem.solution_dir / config.test_cases_filename).read_text())
    if not (filtered := [tc for tc in test_cases if tc['answer'] is not None]):
        style = 'error' if filter_null_answers else 'warning'
        console.print(f'[{style}]{style}:[/{style}] no test cases with answer found for '
                      f'[accent]problem {problem.number}[/accent]')
    expected_types: set[type] = {type(tc['answer']) for tc in filtered}
    if len(expected_types) > 1:
        console.print(f'[error]error:[/error] multiple answer types in test cases for '
                      f'[accent]problem {problem.number}[/accent]: {expected_types}')
        return []
    return filtered if filter_null_answers else test_cases


def generate_c_code(model: Model, *, problem: Problem, force: bool, major: bool) -> bool | None:
    """
    Generates C code for Python solutions in the current workspace.

    This function identifies Python solution files in the workspace that do not have corresponding
    C implementation files. It generates C code for these Python solutions based on the test cases
    and problem metadata. The C solutions are created using a templated approach and validated through
    specific criteria.

    Errors during the process, such as template parsing failures or missing test cases with answers,
    are handled, and appropriate messages are logged.

    Arguments:
        model (Model)     : The model instance to use for generating the C solutions.
        problem (Problem) : The problem currently in the workspace.
        force (bool)      : If True, forces generation even if no files are missing.
        major (bool)      : Whether this is after a major change.

    Returns:
        bool | None: Returns True if the C code generation process completes successfully.
                     Returns False if there are errors during the process.
                     Returns None if there are no files to generate.
    """
    if major:
        console.print('[muted]Use structural code transformation for migration after major change.[/muted]')
        return None
    if not (test_cases := _load_test_cases(problem, filter_null_answers=True)):
        return None
    py_solutions: set[str] = {f.stem for f in iterdir_recursive(problem.solution_dir, rt='path') if f.suffix == '.py'}
    c_solutions: set[str] = {f.stem for f in iterdir_recursive(problem.solution_dir, rt='path') if f.suffix == '.c'}
    files_to_generate: str = ' '.join(f'{f}.c' for f in py_solutions if f not in c_solutions)
    if not (force or files_to_generate):
        console.print('[muted]No C solutions to generate.[/muted]')
        return None
    try:
        facts: Facts = gather_facts(strict=True)
    except ValueError as e:
        console.print(f'[error]error:[/error] could not generate C: {e}')
        return False
    solution_template: str = get_template(Templates.NEW_C).substitute(problem=problem.as_title())
    try:
        prompt = filled_template(
            Templates.PROMPT_C,
            facts=facts,
            files_to_generate=files_to_generate,
            solution_template=format_solutions_markdown({'template.c': solution_template}),
        )
    except (KeyError, ValueError) as e:
        console.print(f'[error]error:[/error] template parsing error for '
                      f'[accent]problem {problem.number}[/accent]: {e}')
        return False
    return _generate_code(
        model=model,
        problem=problem,
        label='c code',
        prompt=prompt,
        retry_missing=partial(_retry_missing_message, files_to_generate=files_to_generate),
        validator=partial(_check_generated_code, problem=problem, test_cases=test_cases),
        images=facts.images,
    )


def generate_py_code(model: Model, *, problem: Problem, force: bool, major: bool) -> bool | None:
    """
    Generates Python code for a specified problem using the provided model. The function creates a new file in the
    workspace with a unique name, gathers problem-related facts, and formulates a completion prompt for generating
    solutions. It verifies the presence of problem content and valid test cases before code generation. The function
    also handles template parsing errors and prompts for retry messages when required.

    Parameters:
        model (Model)     : The AI model to use for generating the code.
        problem (Problem) : The problem currently in the workspace.
        force (bool)      : Whether to force the code generation process.
        major (bool)      : Whether this is after a major change.

    Returns:
        bool | None: True if code generation is successful, False if an error or validation issue occurs, or None if
        the workspace is uninitialized.
    """
    if major:
        console.print('[muted]Use structural code transformation for migration after major change.[/muted]')
        return None
    if not (test_cases := _load_test_cases(problem, filter_null_answers=False)):
        return None
    num_existing: int = sum(1 for s in problem.solution_dir.iterdir() if s.is_file() and s.suffix == '.py')
    if not force and num_existing == 0:
        console.print('[muted]No python solutions; solve the problem first[/muted]')
        return None
    file_to_generate: str = f'p{problem.number:04d}_s{num_existing}.py'
    try:
        facts: Facts = gather_facts(strict=not force)
    except ValueError as e:
        console.print(f'[error]error:[/error] could not generate py: {e}')
        return False
    if not facts.problem_content:
        console.print(f'[error]error:[/error] no problem content found for '
                      f'[accent]problem {problem.number}[/accent]')
        return False
    solution_template: str = get_template(Templates.NEW_PY).substitute(problem=problem.as_title())
    try:
        prompt = filled_template(
            Templates.PROMPT_PY,
            facts=facts,
            file_to_generate=file_to_generate,
            solution_template=format_solutions_markdown({'template.py': solution_template}),
        )
    except (KeyError, ValueError) as e:
        console.print(f'[error]error:[/error] template parsing error for '
                      f'[accent]problem {problem.number}[/accent]: {e}')
        return False
    return _generate_code(
        model=model,
        problem=problem,
        label='py code',
        prompt=prompt,
        retry_missing=partial(_retry_missing_message, files_to_generate=file_to_generate),
        validator=partial(_check_generated_code, problem=problem, test_cases=test_cases),
        images=facts.images,
    )


def document_code(model: Model, *, problem: Problem, force: bool, major: bool) -> bool | None:
    """
    Refresh the in-source documentation of every solution in the workspace, leveraging AI.

    This is the API counterpart of the claude-euler-solver skill's `document` action: it re-emits
    each `pNNNN_sK.py` / `.c` with improved module/function docstrings and comments while leaving
    the algorithm and behaviour untouched, then re-checks functional validity exactly as code
    generation does - compiling each C file, header-checking each Python file, and running every
    answered test case. A file that no longer passes its test cases is rejected and rolled back, so
    a documentation pass can never silently change what a solution computes.

    Arguments:
        model (Model)     : The model instance to use for re-documenting the solutions.
        problem (Problem) : The problem currently in the workspace.
        force (bool)      : Accepted for the common generator signature; documentation always runs over
                            the existing solutions.
        major (bool)      : Accepted for the common generator signature; unused here.

    Returns:
        bool | None: True if all solutions were re-documented and re-validated successfully,
                     False on a generation, validation, or setup error,
                     None if there are no solutions to document.
    """
    if major:
        console.print('[muted]Use structural code transformation for migration after major change.[/muted]')
        return None
    if not (force or problem.number in set(p.number for p in problems.solved_problems)):
        console.print('[muted]Use [accent]--force[/accent] to re-document solutions.[/muted]')
        return None
    if not (test_cases := _load_test_cases(problem, filter_null_answers=True)):
        return None
    files_to_generate: str = ' '.join(sorted(
        f.name for f in iterdir_recursive(problem.solution_dir, rt='path') if f.suffix in ('.py', '.c')))
    if not files_to_generate:
        console.print('[muted]No solutions to document.[/muted]')
        return None
    try:
        facts: Facts = gather_facts(strict=True)
    except ValueError as e:
        console.print(f'[error]error:[/error] could not document solutions: {e}')
        return False
    try:
        prompt = filled_template(
            Templates.PROMPT_DOC,
            facts=facts,
            files_to_generate=files_to_generate,
        )
    except (KeyError, ValueError) as e:
        console.print(f'[error]error:[/error] template parsing error for '
                      f'[accent]problem {problem.number}[/accent]: {e}')
        return False
    return _generate_code(
        model=model,
        problem=problem,
        label='doc',
        prompt=prompt,
        retry_missing=partial(_retry_missing_message, files_to_generate=files_to_generate),
        validator=partial(_check_generated_code, problem=problem, test_cases=test_cases),
        images=facts.images,
    )
