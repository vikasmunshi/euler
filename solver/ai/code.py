#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Module to generate C solutions from Python solutions, leveraging AI."""
from __future__ import annotations

from ast import literal_eval
from functools import partial
from json import loads
from pathlib import Path
from re import DOTALL, MULTILINE, compile as re_compile
from subprocess import TimeoutExpired, run
from typing import Any, Callable, NamedTuple, Protocol, runtime_checkable

from anthropic import APIError
from anthropic.types import MessageParam

from solver.ai.facts import Facts, format_solutions_markdown, gather_facts, prepare_anthropic_request
from solver.ai.models import Model, record_usage
from solver.config import config
from solver.core.lock import check_workspace, check_workspace_lock
from solver.core.problems import Problem
from solver.shell import console
from solver.templates.engine import Templates, filled_template, get_template
from solver.utils.path_utils import canonical_path, iterdir_recursive, write_file

max_retries: int = 5
max_output_tokens: int = 32_000
api_timeout: float = 600.0  # seconds


def retry_missing_message(truncated: bool, files_to_generate: str) -> str:
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

    @staticmethod
    def from_msg(msg: str) -> list[Solution]:
        """Parse solutions from an AI response containing // BEGIN / // END delimiters."""
        pattern = re_compile(r'^// BEGIN (\S+)\n(.*?)\n// END \1', MULTILINE | DOTALL)
        return [Solution(name=m.group(1), code=m.group(2)) for m in pattern.finditer(msg)]


class SolutionsCheckResults(NamedTuple):
    verdict: bool
    msg: str
    passed: list[str]
    failed: list[str]
    errors: dict[str, str]

    def as_msg(self) -> str:  # TO:DO, modify if required
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


def generate_code(
        model: Model,
        problem: Problem,
        prompt: str,
        retry_missing: Callable[[bool], str],
        validator: Validator,
        images: dict[str, bytes] | None = None,
) -> bool | None:
    """
    Drive a model to generate solutions, retrying on parse or validation failure.

    Args:
        model:          The language model used for generating solutions.
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
        console.print(f'[error]error:[/error] {type(e).__name__} preparing request for problem '
                      f'[accent]{problem.number}[/accent]: {e}')
        return False
    for attempt in range(1, max_retries + 1):
        console.print(f'[primary]Generating solutions for problem [accent]{problem.number}[/accent] '
                      f'(attempt {attempt}/{max_retries})...[/primary]')
        try:
            with client.messages.stream(model=model,
                                        max_tokens=max_output_tokens,
                                        system=system_blocks,
                                        messages=messages,
                                        timeout=api_timeout) as stream:
                response = stream.get_final_message()
        except APIError as e:
            console.print(f'[error]error:[/error] Anthropic API error for problem '
                          f'[accent]{problem.number}[/accent]: {e}')
            return False
        record_usage(model, response.usage)
        usage = response.usage
        console.print(f'[muted]Tokens used for problem [accent]{problem.number}[/accent]: '
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
            console.print(f'[error]error:[/error] no text block in response for problem '
                          f'[accent]{problem.number}[/accent]')
            return False
        solutions = Solution.from_msg(text)
        if not solutions:
            console.print(f'[error]error:[/error] could not parse any solutions from response for problem '
                          f'[accent]{problem.number}[/accent]')
            if attempt < max_retries:
                retry_msg = retry_missing(truncated)
                messages.append(MessageParam(role='assistant', content=text))
                messages.append(MessageParam(role='user', content=retry_msg, ))
            continue
        result = validator(attempt=attempt, solutions=solutions)
        if result.verdict:
            return True
        if attempt < max_retries:
            messages.append(MessageParam(role='assistant', content=text))
            messages.append(MessageParam(
                role='user',
                content=(f'The following solutions failed validation:\n'
                         f'{','.join(result.failed)}\n\n'
                         f'Please fix only the failed solutions '
                         f'and return them in the same // BEGIN / // END format.\n\n'
                         f'{result.as_msg()}'),
            ))
    console.print(f'[error]error:[/error] failed to generate valid solutions for problem '
                  f'[accent]{problem.number}[/accent] '
                  f'after {max_retries} attempts')
    return False


def check_solution_against_test_cases(*,
                                      executable_file: Path,
                                      test_cases: list[dict[str, Any]],
                                      passed: set[str],
                                      failed: set[str],
                                      errors: dict[str, str],
                                      expected_type: type,
                                      ) -> None:
    name = executable_file.name
    timeout = config.timeout_single
    for test_case in test_cases:
        category: str = test_case['category']
        input_args: list[str] = [str(v) for v in test_case['input'].values()]
        expected: Any | None = test_case['answer']
        cmdline = [f'{executable_file}', *input_args, '--runs=1']
        try:
            process = run(
                cmdline,
                capture_output=True,
                text=True,
                cwd=config.root_dir,
                timeout=timeout,
            )
        except TimeoutExpired as e:
            console.print(f'cmdline: {" ".join(cmdline)}\nrc: -1\nstdout:\n\nstderr:\n{e}\n',
                          markup=False, highlight=False)
            errors[name] = (f'#### cmdline:\n\n{' '.join(cmdline)}\n\n'
                            f'#### error:\n\ncmd did not complete within timeout of '
                            f'{timeout} seconds\n\n'
                            f'#### stdout:\n\n{(e.stdout or b'').decode()}\n\n'
                            f'#### stderr:\n\n{(e.stderr or b'').decode()}\n\n')
            if test_case['category'] in ('dev', 'main'):
                failed.add(name)
            continue
        else:
            console.print(f'cmdline: {" ".join(cmdline)}\nrc: {process.returncode}\n'
                          f'stdout:\n{process.stdout}\nstderr:\n{process.stderr}\n',
                          markup=False, highlight=False)
        if process.returncode != 0:
            failed.add(name)
            errors[name] = (f'#### cmdline:\n\n{' '.join(cmdline)}\n\n'
                            f'#### error:\n\nprocess returned non-zero exit code {process.returncode}\n\n'
                            f'#### stdout:\n\n{process.stdout}\n\n'
                            f'#### stderr:\n\n{process.stderr}\n\n')
            break
        try:
            _runs, _average, _answer = process.stdout.splitlines()[-1].split(' ', maxsplit=2)
            answer = literal_eval(_answer) if expected_type in (list, tuple, dict) else expected_type(_answer)
            if category == 'main' and expected is None:
                console.print(f'[accent]{executable_file.name} {input_args} -> [bold]{_answer}[/bold][/accent]')
                assert console.input('is this correct? (y/n) ')[0].lower() == 'y', f'answer {_answer} is incorrect.'
            if expected is not None:
                assert answer == expected, f'incorrect answer {_answer}, expected {expected}'
        except (AssertionError, IndexError, ValueError) as err:
            failed.add(name)
            existing_error = errors.get(name, '')
            existing_error = existing_error + ('\n\n' if existing_error else '')
            errors[name] = existing_error + (f'#### cmdline:\n\n{' '.join(cmdline)}\n\n'
                                             f'#### error:\n\n{err}\n\n'
                                             f'#### stdout:\n\n{process.stdout}\n\n'
                                             f'#### stderr:\n\n{process.stderr}\n\n')
    if name not in failed:
        passed.add(name)


def check_results(*,
                  passed: set[str],
                  failed: set[str],
                  errors: dict[str, str],
                  ) -> SolutionsCheckResults:
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


@check_workspace_lock
def check_generated_c_code(*,
                           attempt: int,
                           solutions: list[Solution],
                           test_cases: list[dict[str, Any]],
                           expected_type: type,
                           ) -> SolutionsCheckResults:
    """Check if the C solutions for a problem are valid."""
    if not solutions:
        return SolutionsCheckResults(verdict=False, msg='No solutions found', passed=[], failed=[], errors={})
    passed: set[str] = set()
    failed: set[str] = set()
    errors: dict[str, str] = {}
    for solution in solutions:
        name: str = solution.name
        code: bytes = solution.code.encode()
        source_file: Path = config.workspace_dir / name
        if source_file.suffix != '.c':
            failed.add(name)
            errors[name] = f'{name} is not a valid C source filename, should end with .c'
            continue
        write_file(source_file, code, f'trying solution {name}...')
        cmdline: list[str] = [config.scripts.build_c, canonical_path(source_file)]
        process = run(cmdline, capture_output=True, text=True, cwd=config.root_dir)
        console.print(f'cmdline: {" ".join(cmdline)}\nrc: {process.returncode}\n'
                      f'stdout:\n{process.stdout}\nstderr:\n{process.stderr}\n',
                      markup=False, highlight=False)
        if process.returncode != 0:
            failed.add(name)
            errors[name] = (f'#### cmdline:\n\n{' '.join(cmdline)}\n\n'
                            f'#### error:\n\ncompilation failed\n\n'
                            f'#### stdout:\n\n{process.stdout}\n\n'
                            f'#### stderr:\n\n{process.stderr}\n\n')
            continue
        executable_file: Path = config.workspace_dir / f'{source_file.stem}_c'
        check_solution_against_test_cases(
            executable_file=executable_file,
            test_cases=test_cases,
            passed=passed,
            failed=failed,
            errors=errors,
            expected_type=expected_type,
        )
        if name in failed:
            source_file.unlink(missing_ok=True)
            write_file(source_file.with_suffix(f'.c.{attempt}.bak'), code, f'failed {name}')
    return check_results(passed=passed, failed=failed, errors=errors, )


@check_workspace_lock
def check_generated_py_code(*,
                            attempt: int,
                            solutions: list[Solution],
                            test_cases: list[dict[str, Any]],
                            expected_type: type,
                            ) -> SolutionsCheckResults:
    """Check if the py solutions for a problem are valid."""
    if not solutions:
        return SolutionsCheckResults(verdict=False, msg='No solutions found', passed=[], failed=[], errors={})
    passed: set[str] = set()
    failed: set[str] = set()
    errors: dict[str, str] = {}
    for solution in solutions:
        name: str = solution.name
        code: bytes = solution.code.encode()
        source_file: Path = config.workspace_dir / name
        if source_file.suffix != '.py':
            failed.add(name)
            errors[name] = f'{name} is not a valid PY source filename, should end with .py'
            continue
        # Validate the first two header lines exactly as the prompt and `new.py` template mandate:
        # line 1 is the python3.14 shebang, line 2 is the UTF-8 coding declaration.
        expected_header: tuple[str, str] = ('#!/usr/bin/env python3.14', '# -*- coding: utf-8 -*-')
        header_lines: list[str] = solution.code.split('\n', 2)[:2]
        actual_header: tuple[str, ...] = tuple(line.rstrip() for line in header_lines)
        if actual_header != expected_header:
            failed.add(name)
            errors[name] = (f'{name} does not have the required header. '
                            f'Expected first two lines to be {list(expected_header)!r}, '
                            f'got {list(actual_header)!r}')
            continue
        write_file(source_file, code, f'trying solution {name}...')
        source_file.chmod(0o755)
        executable_file: Path = source_file
        check_solution_against_test_cases(
            executable_file=executable_file,
            test_cases=test_cases,
            passed=passed,
            failed=failed,
            errors=errors,
            expected_type=expected_type,
        )
        if name in failed:
            source_file.unlink(missing_ok=True)
            write_file(source_file.with_suffix(f'.py.{attempt}.bak'), code, f'failed {name}')
    return check_results(passed=passed, failed=failed, errors=errors, )


@check_workspace
def generate_c_code(model: Model, *, force: bool, major: bool) -> bool | None:
    """
    Generates C code for Python solutions in the current workspace.

    This function identifies Python solution files in the workspace that do not have corresponding
    C implementation files. It generates C code for these Python solutions based on the test cases
    and problem metadata. The C solutions are created using a templated approach and validated through
    specific criteria.

    Errors during the process, such as template parsing failures or missing test cases with answers,
    are handled, and appropriate messages are logged.

    Arguments:
        model (Model):  The model instance to use for generating the C solutions.
        force (bool):   If True, forces generation even if no files are missing.
        major (bool):   Whether this is after a major change.

    Returns:
        bool | None: Returns True if the C code generation process completes successfully.
                     Returns False if there are errors during the process.
                     Returns None if there are no files to generate.
    """
    if major:
        console.print('[muted]Use structural code transformation for migration after major change.[/muted]')
        return None
    py_solutions: set[str] = {f.stem for f in iterdir_recursive(config.workspace_dir, rt='path') if f.suffix == '.py'}
    c_solutions: set[str] = {f.stem for f in iterdir_recursive(config.workspace_dir, rt='path') if f.suffix == '.c'}
    files_to_generate: str = ' '.join(f'{f}.c' for f in py_solutions if f not in c_solutions)
    if not (force or files_to_generate):
        console.print('[muted]No C solutions to generate.[/muted]')
        return None
    try:
        facts: Facts = gather_facts(strict=True)
    except ValueError as e:
        console.print(f'[error]error:[/error] could not generate C: {e}')
        return False
    if (problem := Problem.from_workspace()) is None:
        console.print('[muted]Use [accent]init[/accent] to initialize the workspace first.[/muted]')
        return None
    solution_template: str = get_template(Templates.NEW_C).substitute(problem=problem.as_title())
    try:
        prompt = filled_template(
            Templates.PROMPT_C,
            facts=facts,
            files_to_generate=files_to_generate,
            solution_template=format_solutions_markdown({'template.c': solution_template}),
        )
    except (KeyError, ValueError) as e:
        console.print(f'[error]error:[/error] template parsing error for problem '
                      f'[accent]{problem.number}[/accent]: {e}')
        return False
    test_cases: list[dict[str, Any]] = loads((config.workspace_dir / config.test_cases_filename).read_text())
    test_cases = [tc for tc in test_cases if tc['answer'] is not None]
    if not test_cases:
        console.print(f'[error]error:[/error] no test cases with answer found for problem '
                      f'[accent]{problem.number}[/accent]')
        return False
    expected_types: set[type] = {type(tc['answer']) for tc in test_cases}
    if len(expected_types) != 1:
        console.print(f'[error]error:[/error] multiple answer types in test cases for problem '
                      f'[accent]{problem.number}[/accent]: {expected_types}')
        return False
    expected_type: type = expected_types.pop()

    return generate_code(
        model=model,
        problem=problem,
        prompt=prompt,
        retry_missing=partial(retry_missing_message, files_to_generate=files_to_generate),
        validator=partial(check_generated_c_code, test_cases=test_cases, expected_type=expected_type),
        images=facts.images,
    )


@check_workspace
def generate_py_code(model: Model, *, force: bool, major: bool) -> bool | None:
    """
    Generates Python code for a specified problem using the provided model. The function creates a new file in the
    workspace with a unique name, gathers problem-related facts, and formulates a completion prompt for generating
    solutions. It verifies the presence of problem content and valid test cases before code generation. The function
    also handles template parsing errors and prompts for retry messages when required.

    Parameters:
        model (Model): The AI model to use for generating the code.
        force (bool): Whether to force the code generation process.
        major (bool): Whether this is after a major change.

    Returns:
        bool | None: True if code generation is successful, False if an error or validation issue occurs, or None if
        the workspace is uninitialized.
    """
    if major:
        console.print('[muted]Use structural code transformation for migration after major change.[/muted]')
        return None
    num_existing: int = sum(1 for s in config.workspace_dir.iterdir() if s.is_file() and s.suffix == '.py')
    if not force and num_existing == 0:
        console.print('[muted]No python solutions; solve the problem first[/muted]')
        return None
    if (problem := Problem.from_workspace()) is None:
        console.print('[muted]Use [accent]init[/accent] to initialize the workspace first.[/muted]')
        return None
    file_to_generate: str = f'p{problem.number:04d}_s{num_existing}.py'
    try:
        facts: Facts = gather_facts(strict=not force)
    except ValueError as e:
        console.print(f'[error]error:[/error] could not generate py: {e}')
        return False
    if not facts.problem_content:
        console.print(f'[error]error:[/error] no problem content found for problem [accent]{problem.number}[/accent]')
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
        console.print(f'[error]error:[/error] template parsing error for problem '
                      f'[accent]{problem.number}[/accent]: {e}')
        return False
    test_cases: list[dict[str, Any]] = loads((config.workspace_dir / config.test_cases_filename).read_text())
    if not [tc for tc in test_cases if tc['answer'] is not None]:
        console.print(f'[error]error:[/error] no test cases with answer found for problem '
                      f'[accent]{problem.number}[/accent]')
        return False
    expected_type: type = next(type(tc['answer']) for tc in test_cases if tc['answer'] is not None)

    return generate_code(
        model=model,
        problem=problem,
        prompt=prompt,
        retry_missing=partial(retry_missing_message, files_to_generate=file_to_generate),
        validator=partial(check_generated_py_code, test_cases=test_cases, expected_type=expected_type),
        images=facts.images,
    )


__all__ = ('generate_c_code', 'generate_py_code')
