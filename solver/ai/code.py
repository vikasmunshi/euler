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

from anthropic import Anthropic
from anthropic.types import MessageParam

from solver.ai.facts import Facts, format_solutions_markdown, gather_facts
from solver.ai.models import Model, consumed_tokens, get_api_key
from solver.core.config import Config
from solver.core.problems import Problem
from solver.core.stack import read_stack_file
from solver.core.templates import Templates, filled_template, get_template
from solver.core.workspace import stack_the_workspace
from solver.utils.path_utils import canonical_path, iterdir_recursive, write_file
from solver.utils.workspace import check_workspace_lock

max_retries: int = 5


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
        This function checks the solutions for a specific problem and returns the result of the verification.

        Args:
            attempt:        The current attempt number for solution verification.
            solutions:      A list of Solution objects to be verified.
            test_cases:     A list of test cases for the problem.

        Returns:
            A CheckSolutionsResult object containing the result of the solution verification process.
        """
        ...


@check_workspace_lock
def generate_code(
        model: Model,
        problem: Problem,
        prompt: str,
        retry_missing: Callable[[bool], str],
        validator: Validator,
) -> bool | None:
    """
    Decorator to ensure the workspace is locked before executing the function.

    Args:
        model:          The language model used for generating C solutions.
        problem:        The problem for which solutions are being generated.
        prompt:         Template prompt to guide the model's solution generation.
        retry_missing:  Function to generate a retry message for missing solutions
                        differentiated based on if stop_reason was max_tokens.
        test_cases:     Test cases for validating generated solutions.
        validator:      Instance of Validator used for validating generated solutions.

    Returns:
        bool: True if C solutions were successfully generated and validated,
        None if no workspace is initialized or no solutions need generation,
        False on generation or validation failure.
    """

    client = Anthropic(api_key=get_api_key())
    messages: list[MessageParam] = [MessageParam(role='user', content=prompt)]
    for attempt in range(1, max_retries + 1):
        print(f'Generating solutions for problem {problem.number} (attempt {attempt}/{max_retries})...')
        response = client.messages.create(model=model, max_tokens=16384, messages=messages)
        consumed_tokens[model]['input'] += response.usage.input_tokens
        consumed_tokens[model]['output'] += response.usage.output_tokens
        print(f'Tokens used for problem {problem.number}: '
              f'input {response.usage.input_tokens}, output {response.usage.output_tokens}, '
              f'stop_reason {response.stop_reason!r}')
        truncated: bool = response.stop_reason == 'max_tokens'
        if truncated:
            print(f'Warning: max_tokens reached for problem {problem.number}; response may be truncated')
        text: str | None = next((b.text for b in response.content if b.type == 'text'), None)
        if text is None:
            print(f'Error: no text block in response for problem {problem.number}')
            return False
        solutions = Solution.from_msg(text)
        if not solutions:
            print(f'Error: could not parse any solutions from response for problem {problem.number}')
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
    print(f'Failed to generate valid solutions for problem {problem.number} after {max_retries} attempts')
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
    for test_case in test_cases:
        input_args: list[str] = [str(v) for v in test_case['input'].values()]
        expected: Any | None = test_case['answer']
        cmdline = [f'{executable_file}', *input_args, '--runs=1']
        try:
            process = run(
                cmdline,
                capture_output=True,
                text=True,
                cwd=Config.root_dir,
                timeout=Config.timeout_single,
            )
        except TimeoutExpired as e:
            print(f'cmdline: {' '.join(cmdline)}\n'
                  f'rc: -1\n'
                  f'stdout:\n\n'
                  f'stderr:\n{e}\n')
            errors[name] = (f'#### cmdline:\n\n{' '.join(cmdline)}\n\n'
                            f'#### error:\n\ncmd did not complete within timeout of '
                            f'{Config.timeout_single} seconds\n\n'
                            f'#### stdout:\n\n{(e.stdout or b'').decode()}\n\n'
                            f'#### stderr:\n\n{(e.stderr or b'').decode()}\n\n')
            if test_case['category'] in ('dev', 'main'):
                failed.add(name)
            continue
        else:
            print(f'cmdline: {' '.join(cmdline)}\n'
                  f'rc: {process.returncode}\n'
                  f'stdout:\n{process.stdout}\n'
                  f'stderr:\n{process.stderr}\n')
        if process.returncode != 0:
            failed.add(name)
            errors[name] = (f'#### cmdline:\n\n{' '.join(cmdline)}\n\n'
                            f'#### error:\n\nprocess returned non-zero exit code {process.returncode}\n\n'
                            f'#### stdout:\n\n{process.stdout}\n\n'
                            f'#### stderr:\n\n{process.stderr}\n\n')
            break
        _runs, _average, _answer = process.stdout.splitlines()[-1].split(' ', maxsplit=2)
        try:
            answer = literal_eval(_answer) if expected_type in (list, tuple, dict) else expected_type(_answer)
            if expected is not None:
                assert answer == expected, f'incorrect answer {_answer}, expected {expected}'
        except (AssertionError, ValueError) as err:
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
        stack_the_workspace()
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
        source_file: Path = Config.workspace_dir / name
        if source_file.suffix != '.c':
            failed.add(name)
            errors[name] = f'{name} is not a valid C source filename, should end with .c'
            continue
        write_file(source_file, code, f'trying solution {name}...')
        cmdline: list[str] = [Config.ScriptPaths.BUILD_C, canonical_path(source_file)]
        process = run(cmdline, capture_output=True, text=True, cwd=Config.root_dir)
        print(f'cmdline: {' '.join(cmdline)}\n'
              f'rc: {process.returncode}\n'
              f'stdout:\n{process.stdout}\n'
              f'stderr:\n{process.stderr}\n')
        if process.returncode != 0:
            failed.add(name)
            errors[name] = (f'#### cmdline:\n\n{' '.join(cmdline)}\n\n'
                            f'#### error:\n\ncompilation failed\n\n'
                            f'#### stdout:\n\n{process.stdout}\n\n'
                            f'#### stderr:\n\n{process.stderr}\n\n')
            continue
        executable_file: Path = Config.workspace_dir / f'{source_file.stem}_c'
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
        source_file: Path = Config.workspace_dir / name
        if source_file.suffix != '.py':
            failed.add(name)
            errors[name] = f'{name} is not a valid PY source filename, should end with .py'
            continue
        # Check first line is a valid Python shebang
        first_line = solution.code.split('\n', 1)[0].strip()
        valid_shebangs = ('#!/usr/bin/env python3', '#!/usr/bin/env python3.14')
        if not any(first_line == shebang for shebang in valid_shebangs):
            failed.add(name)
            errors[name] = (f'{name} does not have a valid Python shebang as first line. '
                            f'Expected one of {valid_shebangs}, got: {first_line!r}')
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


@check_workspace_lock
def generate_c_code(model: Model, force: bool = False) -> bool | None:
    """
    Generates C code for Python solutions in the current workspace.

    This function identifies Python solution files in the workspace that do not have corresponding
    C implementation files. It generates C code for these Python solutions based on the test cases
    and problem metadata. The C solutions are created using a templated approach and validated through
    specific criteria.

    Errors during the process, such as template parsing failures or missing test cases with answers,
    are handled, and appropriate messages are logged.

    Arguments:
        model (Model): The model instance to use for generating the C solutions.
        force (bool): If True, forces generation even if no files are missing. Defaults to False.

    Returns:
        bool | None: Returns True if the C code generation process completes successfully.
                     Returns False if there are errors during the process.
                     Returns None if there are no files to generate.
    """
    if (problem := Problem.from_workspace()) is None:
        print('No workspace initialized. Use init to initialize the workspace')
        return None
    py_solutions: set[str] = {f.stem for f in iterdir_recursive(Config.workspace_dir, rt='path') if f.suffix == '.py'}
    c_solutions: set[str] = {f.stem for f in iterdir_recursive(Config.workspace_dir, rt='path') if f.suffix == '.c'}
    files_to_generate: str = ' '.join(f'{f}.c' for f in py_solutions if f not in c_solutions)
    if not (force or files_to_generate):
        print(f'No C solutions to generate for problem {problem.number}')
        return None
    try:
        facts: Facts = gather_facts(problem.number, strict=True)
    except ValueError as e:
        print(f'Error: could not generate c for problem {problem.number}: {e}')
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
        print(f'Error: Template parsing error while generating notes for problem {problem.number}: {e}')
        return False
    test_cases: list[dict[str, Any]] = loads(read_stack_file(problem.number, Config.test_cases_filename)[0])
    test_cases = [tc for tc in test_cases if tc['answer'] is not None]
    if not test_cases:
        print(f'No test cases with answer found for problem {problem.number}')
        return False
    expected_types: set[type] = {type(tc['answer']) for tc in test_cases}
    if len(expected_types) != 1:
        print(f'Multiple types of answers found in test cases for problem {problem.number}: {expected_types}')
        return False
    expected_type: type = expected_types.pop()

    def retry_message(truncated: bool) -> str:
        if truncated:
            reason = 'Your previous response was truncated before any complete solution block was emitted.'
        else:
            reason = 'Your previous response did not contain any valid solution blocks.'
        return (f'{reason} '
                f'Please output all required solutions using the // BEGIN / // END format, '
                f'ensuring each block is fully closed.\n\n'
                f'Files to generate: {files_to_generate}')

    return generate_code(
        model=model,
        problem=problem,
        prompt=prompt,
        retry_missing=retry_message,
        validator=partial(check_generated_c_code, test_cases=test_cases, expected_type=expected_type),
    )


@check_workspace_lock
def generate_py_code(model: Model, force: bool = False) -> bool | None:
    """
    Generates Python code for a specified problem using the provided model. The function creates a new file in the
    workspace with a unique name, gathers problem-related facts, and formulates a completion prompt for generating
    solutions. It verifies the presence of problem content and valid test cases before code generation. The function
    also handles template parsing errors and prompts for retry messages when required.

    Parameters:
        model (Model): The AI model to use for generating the code.
        force (bool): Whether to force the code generation process, default is False.

    Returns:
        bool | None: True if code generation is successful, False if an error or validation issue occurs, or None if
        the workspace is uninitialized.
    """
    if (problem := Problem.from_workspace()) is None:
        print('No workspace initialized. Use init to initialize the workspace')
        return None
    num_existing: int = sum(1 for s in Config.workspace_dir.iterdir() if s.is_file() and s.suffix == '.py')
    if not force and num_existing > 0:
        print(f'Found {num_existing} existing solution files for problem {problem.number}.')
        return None
    file_to_generate: str = f'p{problem.number:04d}_s{num_existing}.py'
    facts: Facts = gather_facts(problem.number, strict=False)
    if not facts.problem_content:
        print(f'No problem content found for problem {problem.number}')
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
        print(f'Error: Template parsing error while generating notes for problem {problem.number}: {e}')
        return False
    test_cases: list[dict[str, Any]] = loads(read_stack_file(problem.number, Config.test_cases_filename)[0])
    if not [tc for tc in test_cases if tc['answer'] is not None]:
        print(f'No test cases with answer found for problem {problem.number}')
        return False
    expected_type: type = next(type(tc['answer']) for tc in test_cases if tc['answer'] is not None)

    def retry_message(truncated: bool) -> str:
        if truncated:
            reason = 'Your previous response was truncated before any complete solution block was emitted.'
        else:
            reason = 'Your previous response did not contain any valid solution blocks.'
        return (f'{reason} '
                f'Please output all required solutions using the // BEGIN / // END format, '
                f'ensuring each block is fully closed.\n\n'
                f'File to generate: {file_to_generate}')

    return generate_code(
        model=model,
        problem=problem,
        prompt=prompt,
        retry_missing=retry_message,
        validator=partial(check_generated_py_code, test_cases=test_cases, expected_type=expected_type),
    )


__all__ = ('generate_c_code', 'generate_py_code')
