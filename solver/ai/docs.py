#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Module to generate notes for solver solutions, leveraging AI. """
from __future__ import annotations

__all__ = ['generate_notes', 'generate_test_cases']

from json import JSONDecodeError, dumps, loads

from anthropic import APIError
from anthropic.types import MessageParam, TextBlock

from solver.ai.facts import Facts, gather_facts, prepare_anthropic_request
from solver.ai.models import Model, record_usage
from solver.config import config
from solver.core.problems import Problem, problems
from solver.shell import console
from solver.templates.engine import Templates, filled_template
from solver.utils.path_utils import write_file

max_output_tokens: int = 32_000
api_timeout: float = 600.0  # seconds
test_cases_retries: int = 2


def _generate_doc(prompt: str, model: Model, images: dict[str, bytes] | None = None,
                  follow_up: str | None = None) -> str | None:
    """
    Generate documentation by streaming from the Anthropic API.

    The leading line of 'prompt' (up to the first blank line) is sent as the system block with an
    ephemeral cache_control marker; the remainder is sent as the user message with the cache marker
    on its trailing content block. When 'follow_up' is provided it is appended as a second user
    turn after a placeholder assistant turn, so the initial system+user prefix is still cached.

    Args:
        prompt:    Combined "<system>\\n\\n<user>" template content.
        model:     The AI model used for generating content.
        images:    Optional map of resource filename to image bytes referenced in the prompt.
        follow_up: Optional follow-up user turn (used for one-shot retries that piggyback on cache).

    Returns:
        The generated text block, or 'None' on API or response errors.
    """
    try:
        client, system_blocks, messages = prepare_anthropic_request(prompt, images)
        if follow_up is not None:
            messages.append(MessageParam(role='assistant', content='(previous attempt produced unparseable output)'))
            messages.append(MessageParam(role='user', content=follow_up))
        with client.messages.stream(
                model=model,
                max_tokens=max_output_tokens,
                system=system_blocks,
                messages=messages,
                timeout=api_timeout,
        ) as stream:
            response = stream.get_final_message()
        usage = response.usage
        console.print(f'[muted]Tokens used: '
                      f'input {usage.input_tokens}, output {usage.output_tokens}, '
                      f'cache_write {getattr(usage, "cache_creation_input_tokens", 0) or 0}, '
                      f'cache_read {getattr(usage, "cache_read_input_tokens", 0) or 0}, '
                      f'stop_reason {response.stop_reason!r}[/muted]')
        record_usage(model, usage)
        if response.stop_reason == 'max_tokens':
            console.print('[warning]Warning: max_tokens reached; response may be truncated[/warning]')
        text_block: TextBlock | None = next(
            (block for block in response.content if block.type == 'text'), None)
        if text_block is None:
            block_types = [block.type for block in response.content]
            console.print(f'[error]error:[/error] no text block in response '
                          f'(stop_reason={response.stop_reason!r}, block types={block_types})')
            return None
        return text_block.text
    except APIError as e:
        console.print(f'[error]error:[/error] Anthropic API error: {e}')
        return None
    except (ValueError, OSError) as e:
        console.print(f'[error]error:[/error] {type(e).__name__} generating notes: {e}')
        return None


def generate_notes(model: Model, *, problem: Problem, force: bool, major: bool) -> bool | None:
    """
    Generate and update HTML notes for the given problem.

    Args:
        model (Model)     : The AI model used to generate notes.
        problem (Problem) : The problem to document.
        force (bool)      : Force note generation even if no new solutions are available.
        major (bool)      : Withhold any prior notes from the prompt (use after a template/prompt change).
    """
    if not (force or problem.number in set(p.number for p in problems.solved_problems)):
        console.print('[muted]Use [accent]--force[/accent] to re-document solutions.[/muted]')
        return None
    try:
        facts: Facts = gather_facts(problem, strict=True)
    except ValueError as e:
        console.print(f'[error]error:[/error] could not document solutions: {e}')
        return False
    if major:
        console.print('[muted]Existing notes withheld.[/muted]')
        facts = Facts(**{k: v for k, v in facts._asdict().items() if k != 'solution_notes'},
                      solution_notes='')
    prompt = filled_template(Templates.PROMPT_NOTES, facts=facts)
    console.print('[primary]Generating notes...[/primary]')
    notes: str | None = _generate_doc(prompt=prompt, model=model, images=facts.images)
    if notes is None:
        console.print('[error]error:[/error] failed to generate notes')
        return False
    write_file(problem.solution_dir / config.notes_filename, notes.encode(),
               f'Updated {config.notes_filename}')
    return True


def _parse_test_cases_json(raw: str) -> str | None:
    """Strip optional markdown code fences and return a re-formatted JSON string, or None on failure."""
    stripped = raw.strip()
    if stripped.startswith('```'):
        stripped = stripped.split('\n', 1)[1].rsplit('```', 1)[0]
    try:
        return dumps(loads(stripped), indent=2)
    except JSONDecodeError:
        return None


def generate_test_cases(model: Model, *, problem: Problem, force: bool, major: bool) -> bool | None:
    """
    Generate a test_cases.json file for the given problem.

    Retries once with a "JSON only, no prose" reminder if the first response cannot be parsed.

    Args:
        model (Model)     : The AI model used to generate test cases.
        problem (Problem) : The problem to generate test cases for.
        force (bool)      : Overwrite an existing test_cases.json.
        major (bool)      : No-op for test cases; preserved for the common make() signature.
    """
    if major:
        console.print('[muted]Use structural transformation for migration after a major change.[/muted]')
        return None
    if not (force or not (problem.solution_dir / config.test_cases_filename).exists()):
        console.print('[muted]Test cases exist.[/muted]')
        return None
    facts: Facts = gather_facts(problem, strict=False)
    prompt = filled_template(Templates.PROMPT_TEST_CASES, facts=facts)
    console.print('[primary]Generating test cases...[/primary]')
    raw: str | None = _generate_doc(prompt=prompt, model=model, images=facts.images)
    parsed: str | None = _parse_test_cases_json(raw) if raw is not None else None
    if parsed is None:
        for attempt in range(1, test_cases_retries + 1):
            console.print(f'[muted]Retrying test-case generation (attempt {attempt}/{test_cases_retries})'
                          f' with strict JSON reminder...[/muted]')
            follow_up = ('Your previous response could not be parsed as JSON. '
                         'Re-emit the entire JSON array only - no markdown, no code fences, no prose, '
                         'no leading or trailing text. The output must start with `[` and end with `]`.')
            raw = _generate_doc(prompt=prompt, model=model, images=facts.images, follow_up=follow_up)
            parsed = _parse_test_cases_json(raw) if raw is not None else None
            if parsed is not None:
                break
    if parsed is None:
        console.print('[error]error:[/error] failed to parse generated test cases JSON')
        if raw is not None:
            console.print(f'Generated test cases: {raw}', markup=False, highlight=False)
        return False
    write_file(problem.solution_dir / config.test_cases_filename, parsed.encode(),
               f'Updated {config.test_cases_filename}')
    return True
