#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Utility function for gathering problem inputs for AI """
from __future__ import annotations

__all__ = ['Facts', 'format_solutions_markdown', 'gather_facts', 'prepare_anthropic_request', 'user_message_content']

from base64 import b64encode
from json import JSONDecodeError, loads
from typing import Any, NamedTuple, cast

from anthropic import Anthropic
from anthropic.types import (Base64ImageSourceParam, CacheControlEphemeralParam, ContentBlockParam,
                             ImageBlockParam, MessageParam, TextBlockParam)

from solver.ai.models import get_api_key
from solver.config import config
from solver.core.problems import problems
from solver.core.results import Result, read_results
from solver.shell.variables import variables
from solver.utils.path_utils import iterdir_recursive

#: Map of file extension (lowercased, no leading dot) to the Anthropic image media type.
#: Only extensions in this map are forwarded as image content blocks to the model.
_IMAGE_MEDIA_TYPES: dict[str, str] = {
    'png': 'image/png',
    'jpg': 'image/jpeg',
    'jpeg': 'image/jpeg',
    'gif': 'image/gif',
    'webp': 'image/webp',
}


class Facts(NamedTuple):
    difficulty: str
    images: dict[str, bytes]
    number: int
    problem_content: str
    problem_resources: dict[str, str]
    results: str
    solution_notes: str
    solutions: str
    solved_date: str
    test_cases: str
    title: str


def format_results_markdown(solved_results: list[Result]) -> str:
    """Render benchmark results as a Markdown table (or a placeholder if empty)."""
    if not solved_results:
        return '(no benchmark results available)'
    rows = ['| solution | category | args | answer | verdict | elapsed (s) |',
            '|---|---|---|---|---|---|']
    for r in solved_results:
        rows.append(f'| {r.solution} | {r.category} | {r.args} | {r.answer} '
                    f'| {r.verdict} | {r.average:.4f} |')
    return '\n'.join(rows)


def format_solutions_markdown(solutions: dict[str, str]) -> str:
    """Render each filename→source pair as a language-tagged Markdown code block."""
    parts: list[str] = []
    for filename, source in solutions.items():
        lang = 'c' if filename.endswith('.c') else 'python'
        parts.append(f'### {filename}\n```{lang}\n{source}\n```')
    return '\n\n'.join(parts)


def format_test_cases_markdown(test_cases: list[dict[str, Any]]) -> str:
    """Render test cases as a Markdown table (or a placeholder if empty)."""
    if not test_cases:
        return '(no test cases available)'
    rows = ['| category | input | answer |', '|---|---|---|']
    for tc in test_cases:
        rows.append(f'| {tc.get("category", "")} | {tc.get("input", "")} | {tc.get("answer", "")} |')
    return '\n'.join(rows)


def gather_facts(strict: bool = False) -> Facts:
    """
    Gathers and processes facts from the 'stack' about a specific problem, including solutions,
    results, test cases, and problem content. This function is used to assemble
    relevant details into a `Facts` object, which contains comprehensive information
    about the problem for further use.

    Arguments:
        strict: If True, enforces strict validation of gathered data
            (e.g., ensures solutions, results, and problem content exist).

    Returns:
        Facts: An object containing all gathered details about the problem,
        including its difficulty, number, title, content, available solutions,
        results, test cases, solution notes, and solved date.

    Raises:
        ValueError: If `strict` is True and any of the required data, such as
        solutions, results, or test cases, is missing or invalid.
    """
    problem = variables.problem
    solutions: dict[str, str] = {}
    for solution in iterdir_recursive(problem.solution_dir, rt='path'):
        if not (solution.suffix in ('.py', '.c')):
            continue
        solutions[solution.name] = solution.read_text()
    if strict and not solutions:
        raise ValueError('No solutions found')
    solved_results: list[Result] = read_results()  # read results from workspace
    if strict and not solved_results:
        raise ValueError('No results found')
    if strict and not [r for r in solved_results if r.verdict == 'correct' and r.category == 'main']:
        raise ValueError('No solved solutions found')
    test_cases: list[dict[str, Any]]
    try:
        test_cases = loads((problem.solution_dir / config.test_cases_filename).read_text())
    except (FileNotFoundError, JSONDecodeError):
        if strict:
            raise ValueError('No test cases found')
        test_cases = []
    if strict:
        if not [tc for tc in test_cases if tc['answer'] is not None]:
            raise ValueError('No test cases with answers found')
    problem_content: str = problem.problem_statement
    images: dict[str, bytes] = {}
    resources: dict[str, str] = {}
    for filename, data in problem.problem_resources.items():
        if filename.rsplit('.', 1)[-1].lower() in _IMAGE_MEDIA_TYPES:
            images[filename] = data
        else:
            resources[filename] = data.decode()
    if not problem_content and strict:
        raise ValueError('No problem content found')
    try:
        solution_notes: str = (problem.solution_dir / config.notes_filename).read_text()
    except FileNotFoundError:
        solution_notes = ''
    solved_date: str = problems.solutions_history.get(problem.number, 'unknown')
    return Facts(
        difficulty=problem.difficulty,
        images=images,
        number=problem.number,
        problem_content=problem_content,
        problem_resources=resources,
        results=format_results_markdown(solved_results),
        solution_notes=solution_notes,
        solutions=format_solutions_markdown(solutions),
        solved_date=solved_date,
        test_cases=format_test_cases_markdown(test_cases),
        title=problem.title,
    )


def user_message_content(user_prompt: str, images: dict[str, bytes], *,
                         cache: bool = False) -> list[ContentBlockParam]:
    """Build a user-message content list of one text block followed by an image block per image.

    Images with unsupported extensions are skipped silently; the model still gets the text and any
    inlined references in "problem_content" point to local resource filenames the AI cannot
    fetch - including the bytes here is what actually lets the model see the image.

    When 'cache' is True, an ephemeral cache_control marker is attached to the final block so
    the API caches everything in this message (and prior system/turns) up to that point. For
    multi-turn retries, only the first user message should set 'cache=True'.
    """
    text_block: TextBlockParam = {'type': 'text', 'text': user_prompt}
    blocks: list[ContentBlockParam] = [text_block]
    for filename, data in images.items():
        media_type = _IMAGE_MEDIA_TYPES.get(filename.rsplit('.', 1)[-1].lower())
        if media_type is None:
            continue
        source: Base64ImageSourceParam = {
            'type': 'base64',
            'media_type': cast(Any, media_type),
            'data': b64encode(data).decode(),
        }
        block: ImageBlockParam = {'type': 'image', 'source': source}
        blocks.append(block)
    if cache and blocks:
        cache_marker: CacheControlEphemeralParam = {'type': 'ephemeral'}
        # TypedDicts permit assigning optional keys; this is the documented placement for
        # attaching cache breakpoints to the trailing content block of a message.
        cast(dict[str, Any], cast(object, blocks[-1]))['cache_control'] = cache_marker
    return blocks


def prepare_anthropic_request(prompt: str, images: dict[str, bytes] | None = None,
                              ) -> tuple[Anthropic, list[TextBlockParam], list[MessageParam]]:
    """Build the standard Anthropic client + cached system/user blocks from a combined prompt.

    The prompt is split at the first markdown heading ('## '): everything above it is the
    system instructions (typically a one-paragraph persona description), everything from the
    heading onward is the user message. This is robust against blank lines inside the system
    block - which the old 'split('\\n\\n')' heuristic silently mishandled - and matches the
    structure every template already uses.

    Both halves carry an ephemeral cache_control breakpoint (system block trailing block;
    final user-content block). Returns '(client, system_blocks, messages)' ready to pass to
    'client.messages.create' or 'client.messages.stream'.

    Raises:
        ValueError: If the prompt has no '## ' heading marking the user portion.
    """
    system_prompt, user_prompt = _split_prompt(prompt)
    client = Anthropic(api_key=get_api_key())
    system_blocks: list[TextBlockParam] = [
        {'type': 'text', 'text': system_prompt, 'cache_control': {'type': 'ephemeral'}},
    ]
    messages: list[MessageParam] = [
        MessageParam(role='user', content=user_message_content(user_prompt, images or {}, cache=True)),
    ]
    return client, system_blocks, messages


def _split_prompt(prompt: str) -> tuple[str, str]:
    """Split a combined prompt into '(system, user)' at the first '## ' heading."""
    marker = '\n## '
    idx = prompt.find(marker)
    if idx == -1:
        raise ValueError('prompt template has no "## " heading; cannot split into system/user')
    return prompt[:idx].rstrip(), prompt[idx + 1:]
