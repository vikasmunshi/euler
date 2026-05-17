#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Module to generate notes for solver solutions, leveraging AI. """
from __future__ import annotations

from json import JSONDecodeError, dumps, loads

from anthropic import Anthropic
from anthropic.types import MessageParam, TextBlock, ThinkingConfigEnabledParam
from bs4 import BeautifulSoup

from solver.ai.facts import Facts, gather_facts
from solver.ai.models import Model, consumed_tokens, get_api_key
from solver.core.config import Config
from solver.core.problems import Problem
from solver.core.stack import has_new_solutions
from solver.core.templates import Templates, filled_template
from solver.core.workspace import reinit_the_workspace, stack_the_workspace
from solver.utils.path_utils import write_file
from solver.utils.workspace import check_workspace_lock


@check_workspace_lock
def _generate_doc(problem_number: int, prompt: str, model: Model) -> str | None:
    """
    Generate documentation based on the specified problem prompt using the Anthropic client and a specified
    AI model. This function manages API interactions, token consumption, and handles potential errors during
    the note generation process.

    Args:
        problem_number (int): The numeric identifier of the problem being processed.
        prompt (str): The prompt content provided to generate the notes.
        model (Model): The AI model used for generating the notes.

    Returns:
        str | None: The textual notes generated for the problem, or None if the generation fails.

    Raises:
        Exception: Captures and logs any error occurring during the process and returns None.
    """
    api_key: str = get_api_key()
    try:
        client = Anthropic(api_key=api_key)
        with client.messages.stream(
                model=model,
                max_tokens=16_000,
                thinking=ThinkingConfigEnabledParam(type='enabled', budget_tokens=10_000),
                messages=[MessageParam(role='user', content=prompt)],
        ) as stream:
            response = stream.get_final_message()
        print(f'Tokens used for problem {problem_number}: '
              f'input {response.usage.input_tokens}, output {response.usage.output_tokens}, '
              f'stop_reason {response.stop_reason!r}')
        consumed_tokens[model]['input'] += response.usage.input_tokens
        consumed_tokens[model]['output'] += response.usage.output_tokens
        if response.stop_reason == 'max_tokens':
            print(f'Warning: max_tokens reached for problem {problem_number}; response may be truncated')
        text_block: TextBlock | None = next(
            (block for block in response.content if block.type == 'text'), None)
        if text_block is None:
            block_types = [block.type for block in response.content]
            print(f'Error: no text block in response for problem {problem_number} '
                  f'(stop_reason={response.stop_reason!r}, block types={block_types})')
            return None
        return text_block.text
    except Exception as e:
        print(f'Error: {type(e).__name__} generating notes for problem {problem_number}: {e}')
        return None


def generate_notes(model: Model, force: bool = False) -> None:
    """
    Generates and updates notes for a specific problem in the workspace.

    This function processes facts about a problem using a pre-defined template
    and a machine learning model to generate solution notes. It updates an HTML
    file within the workspace, appending new content to a specified div element.
    The function performs checks to ensure the workspace is initialized, and only
    proceeds when new solutions are available or when the 'force' parameter is set
    to True. If no relevant div is found in the HTML, the function will warn the
    user and not apply the changes.

    Parameters:
        model (Model):          The machine learning model used to generate notes.
        force (bool, optional): Whether to force note generation even if no new solutions
                                are available (default is False).

    """
    if (problem := Problem.from_workspace()) is None:
        print('No workspace initialized. Use init to initialize the workspace')
        return
    if not (force or has_new_solutions(problem.number)):
        print(f'Problem {problem.number} has no new solutions')
        return
    facts: Facts = gather_facts(problem.number, strict=True)
    prompt = filled_template(Templates.PROMPT_NOTES, facts=facts)
    print(f'Generating notes for problem {problem.number}...')
    notes: str | None = _generate_doc(problem_number=problem.number, prompt=prompt, model=model)
    if notes is None:
        print(f'Error: failed to generate notes for problem {problem.number}')
        return
    current_html: str = (Config.workspace_dir / Config.statement_filename).read_text()
    soup: BeautifulSoup = BeautifulSoup(current_html, 'html.parser')
    if div := soup.find('div', id='solution-notes-content'):
        div.clear()
        div.append(BeautifulSoup(notes, 'html.parser'))
    else:
        print(f'Warning: <div id="solution-notes-content"> not found in problem.html '
              f'for problem {problem.number}; notes not written to file')
        return
    write_file(Config.workspace_dir / Config.statement_filename, str(soup).encode(),
               f'Updated {Config.statement_filename} with generated notes.')
    stack_the_workspace()
    reinit_the_workspace()


def generate_test_cases(model: Model, force: bool = False) -> None:
    """
    Generates test cases for a given problem in the workspace. If the workspace is not
    initialized or test cases already exist for the problem, appropriate messages will
    be printed. This function uses a model to generate test cases based on the facts
    collected for the problem.

    Parameters:
        model (Model):  The model to be used for generating the notes. Defaults to Model.CLAUDE_SONNET_4_6.
        force (bool):   If True, overwrite existing test cases. Defaults to False.

    """
    if (problem := Problem.from_workspace()) is None:
        print('No workspace initialized. Use init to initialize the workspace')
        return
    if not (force or not (Config.workspace_dir / Config.test_cases_filename).exists()):
        print(f'Problem {problem.number} has existing test cases')
        return
    facts: Facts = gather_facts(problem.number, strict=False)
    prompt = filled_template(Templates.PROMPT_TEST_CASES, facts=facts)
    print(f'Generating test cases for problem {problem.number}...')
    test_cases: str | None = _generate_doc(problem_number=problem.number, prompt=prompt, model=model)
    if test_cases is None:
        print(f'Error: failed to generate test cases for problem {problem.number}')
        return
    try:
        # Strip Markdown code fences if present (e.g. ```json ... ```)
        stripped = test_cases.strip()
        if stripped.startswith('```'):
            stripped = stripped.split('\n', 1)[1].rsplit('```', 1)[0]
        test_cases_str: str = dumps(loads(stripped), indent=2)
    except JSONDecodeError:
        print(f'Error: failed to parse generated test cases JSON for problem {problem.number}')
        print(f'Generated test cases: {test_cases}')
        return
    write_file(Config.workspace_dir / Config.test_cases_filename, test_cases_str.encode(),
               f'Updated {Config.test_cases_filename} with generated test cases.')
    stack_the_workspace()


__all__ = ('generate_notes', 'generate_test_cases')
