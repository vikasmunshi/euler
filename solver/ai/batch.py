#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The `claude-batch` command: bulk tag generation over the Message Batches API.

Tagging the whole stack one `claude-api <n> tags` call at a time is ~1000 sequential requests -
hours of wall clock at full list price. This module submits a *wave* of problems as a single
batch job instead, which buys three things:

- **Half price.** Batched tokens bill at 50% of the standard rate.
- **No rate-limit babysitting.** The queue is the API's problem, not a worker pool's.
- **One shared cached prefix.** Every request in a wave carries a byte-identical system block
  (conventions + vocabulary + output contract - see `solver.ai.docs.tags_prompt`), so the whole
  wave reads it from cache instead of re-paying for it ~1000 times. The breakpoint is written
  with a one-hour TTL because a batch can take that long to drain; the default five-minute
  cache would expire mid-wave and silently start re-billing the prefix at full rate.

**Waves, not one big job.** Requests inside a batch cannot see each other's `new-tags`, so a
single 1000-problem job would coin three slugs for the same concept and leave the maintainer to
merge them afterwards. Run a few hundred at a time and reconcile with `update-tags` between
waves; the promoted tags then enter the vocabulary the *next* wave is prompted with.

A submitted wave is recorded in ``<state>/tag_batches.json`` so collection survives a dropped
shell: the job keeps draining server-side regardless, and `claude-batch collect` picks it up.
Results arrive in arbitrary order and are matched back to problems by ``custom_id``.
"""
from __future__ import annotations

__all__ = ['claude_batch']

import time
from collections import Counter
from json import dumps, loads
from typing import Any, Literal

from anthropic import Anthropic
from anthropic.types.message_create_params import MessageCreateParamsNonStreaming
from anthropic.types.messages.batch_create_params import Request

from solver.ai.docs import (_parse_tags_json, enforce_facets, has_solutions,
                            max_output_tokens, tags_prompt)
from solver.ai.facts import Facts, _split_prompt, gather_facts, user_message_content
from solver.ai.models import Model, get_api_key, record_usage
from solver.config import ExitCodes, config
from solver.core.problems import Problem, problems
from solver.shell import console, register
from solver.utils.path_utils import write_file

#: Poll interval while a batch drains. Most batches finish well inside an hour; the API's own
#: ceiling is 24h, so this is a slow poll by design - there is nothing to gain from a tight loop.
poll_seconds: int = 30

#: Where submitted-but-not-yet-collected waves are recorded, so a dropped shell can resume.
_STORE_NAME = 'tag_batches.json'

Target = Literal['solved', 'unsolved', 'untagged', 'all']


def _store_path() -> Any:
    """The per-user batch store path."""
    return config.user_state_dir / _STORE_NAME


def _load_store() -> dict[str, Any]:
    """Read the submitted-wave store (empty when nothing has been submitted yet)."""
    path = _store_path()
    if not path.exists():
        return {}
    try:
        data = loads(path.read_text())
    except ValueError:
        return {}
    return data if isinstance(data, dict) else {}


def _save_store(store: dict[str, Any]) -> None:
    """Persist the submitted-wave store."""
    write_file(_store_path(), dumps(store, indent=2).encode())


def _select(target: Target, limit: int) -> list[Problem]:
    """The problems a wave covers, in problem-number order, capped at ``limit``.

    ``untagged`` is the resumable selector - it skips anything that already has a ``tags.json``,
    so re-running after a partial wave picks up only what is still missing.
    """
    chosen: list[Problem] = []
    for problem in sorted(problems.problems_list, key=lambda p: p.number):
        tagged = (problem.solution_dir / config.tags_filename).exists()
        solved = has_solutions(problem)
        if target == 'solved' and not solved:
            continue
        if target == 'unsolved' and solved:
            continue
        if target == 'untagged' and tagged:
            continue
        chosen.append(problem)
        if len(chosen) >= limit:
            break
    return chosen


def _build_request(problem: Problem, model: Model) -> Request:
    """One batch request for a problem: the shared cached system block plus its own facts.

    The system half is identical for every problem of the same kind, which is the whole point -
    it is what the wave's cache breakpoint covers. Only the user half varies.
    """
    facts: Facts = gather_facts(problem, strict=False)
    system_text, user_text = _split_prompt(tags_prompt(problem, facts))
    return Request(
        custom_id=f'p{problem.number:04d}',
        params=MessageCreateParamsNonStreaming(
            model=model,
            max_tokens=max_output_tokens,
            # A one-hour TTL: a wave can take an hour to drain, and a five-minute breakpoint
            # would lapse partway through and re-bill the prefix at full rate for the remainder.
            system=[{'type': 'text', 'text': system_text,
                     'cache_control': {'type': 'ephemeral', 'ttl': '1h'}}],
            messages=[{'role': 'user', 'content': user_message_content(user_text, facts.images)}],
        ),
    )


def _submit(client: Anthropic, wave: list[Problem], model: Model) -> str:
    """Submit a wave and record it in the store; returns the batch id."""
    console.print(f'[primary]Building {len(wave)} request(s)...[/primary]')
    requests = [_build_request(problem, model) for problem in wave]
    batch = client.messages.batches.create(requests=requests)
    store = _load_store()
    store[batch.id] = {
        'model': str(model),
        'problems': [p.number for p in wave],
        'submitted': time.strftime('%Y-%m-%d %H:%M:%S'),
    }
    _save_store(store)
    console.print(f'[accent]submitted:[/accent] batch [accent]{batch.id}[/accent] '
                  f'({len(wave)} problems) - recorded in {_STORE_NAME}')
    return str(batch.id)


def _wait(client: Anthropic, batch_id: str) -> bool:
    """Poll until the batch ends. Returns False if interrupted (the job keeps draining)."""
    while True:
        batch = client.messages.batches.retrieve(batch_id)
        if batch.processing_status == 'ended':
            return True
        counts = batch.request_counts
        console.print(f'[muted]{batch.processing_status}: {counts.succeeded} done, '
                      f'{counts.processing} processing, {counts.errored} errored[/muted]')
        try:
            time.sleep(poll_seconds)
        except KeyboardInterrupt:
            console.print(f'\n[warning]detached.[/warning] The batch keeps running; collect it with '
                          f'[accent]claude-batch collect --batch-id {batch_id}[/accent]')
            return False


def _collect(client: Anthropic, batch_id: str, model: Model) -> tuple[int, list[str], Counter[str]]:
    """Write every succeeded result to its problem's tags.json.

    Returns ``(written, failures, conflicts)``. ``conflicts`` counts the facet corrections
    `enforce_facets` had to make, tallied by slug across the whole wave - one problem reaching
    for a slug in the wrong facet is a slip, the same slug recurring across a wave is the
    vocabulary telling you the concept is filed under the wrong facet.
    """
    written = 0
    failures: list[str] = []
    conflicts: Counter[str] = Counter()
    for result in client.messages.batches.results(batch_id):
        custom_id = result.custom_id
        if result.result.type != 'succeeded':
            failures.append(f'{custom_id}: {result.result.type}')
            continue
        message = result.result.message
        record_usage(model, message.usage)
        text = next((b.text for b in message.content if b.type == 'text'), None)
        parsed = _parse_tags_json(text) if text is not None else None
        if parsed is None:
            failures.append(f'{custom_id}: unparseable tags JSON')
            continue
        parsed, found = enforce_facets(parsed)
        conflicts.update(found)
        problem = Problem.from_number(int(custom_id.lstrip('p')))
        write_file(problem.solution_dir / config.tags_filename, parsed.encode())
        written += 1
    store = _load_store()
    store.pop(batch_id, None)
    _save_store(store)
    return written, failures, conflicts


@register(requires='maintainer',
          help_text='Generate tags.json for many problems in one Message Batches job.')
def claude_batch(action: Literal['run', 'submit', 'collect', 'list'] = 'run', *,
                 target: Target = 'untagged',
                 limit: int = 250,
                 batch_id: str = '',
                 model: Model = Model.CLAUDE_SONNET_5,
                 ) -> int:
    """Bulk-tag a wave of problems via the Message Batches API (half price, one shared cache).

    Solved problems get the full prompt (domain + per-index techniques + takeaways); unsolved
    ones get the domain-only prompt. Run `update-tags` after each wave to promote the proposed
    `new-tags` before submitting the next, so later waves are prompted with the settled vocabulary.

    Args:
        action:   `run` submits and waits and collects; `submit` returns as soon as the job is
                  queued; `collect` writes the results of an already-submitted job; `list` shows
                  waves that were submitted but not yet collected.
        target:   Which problems to cover - `untagged` (no tags.json yet, the resumable default),
                  `solved`, `unsolved`, or `all`.
        limit:    Maximum problems in this wave. Keep it to a few hundred so that `new-tags`
                  proposals get reconciled often enough to avoid duplicate slugs.
        batch_id: The job to collect (required for `collect`).
        model:    The model to run the wave on.

    Note: the `costs` command counts batched tokens at standard list price, so its total
    overstates a batch wave by roughly 2x; this command prints the true discounted cost.
    """
    if action == 'list':
        store = _load_store()
        if not store:
            console.print('[muted]no submitted batches awaiting collection[/muted]')
            return ExitCodes.EXIT_OK
        for bid, meta in store.items():
            console.print(f'[accent]{bid}[/accent]  {len(meta["problems"])} problems  '
                          f'{meta["model"]}  submitted {meta["submitted"]}')
        return ExitCodes.EXIT_OK

    client = Anthropic(api_key=get_api_key())

    if action == 'collect':
        if not batch_id:
            console.print('[error]error:[/error] collect needs --batch-id (see [accent]claude-batch list[/accent])')
            return ExitCodes.EXIT_ERROR
        meta = _load_store().get(batch_id, {})
        wave_model = Model(meta['model']) if meta.get('model') else model
        if not _wait(client, batch_id):
            return ExitCodes.EXIT_ERROR
        written, failures, conflicts = _collect(client, batch_id, wave_model)
    else:
        wave = _select(target, limit)
        if not wave:
            console.print(f'[muted]nothing to do: no {target} problems[/muted]')
            return ExitCodes.EXIT_OK
        console.print(f'[primary]{len(wave)} problem(s)[/primary] - '
                      f'p{wave[0].number:04d} .. p{wave[-1].number:04d}')
        new_id = _submit(client, wave, model)
        if action == 'submit':
            console.print(f'[muted]collect with [accent]claude-batch collect --batch-id {new_id}[/accent][/muted]')
            return ExitCodes.EXIT_OK
        if not _wait(client, new_id):
            return ExitCodes.EXIT_ERROR
        written, failures, conflicts = _collect(client, new_id, model)

    for failure in failures:
        console.print(f'  [error]•[/error] {failure}')
    for conflict, count in conflicts.most_common():
        console.print(f'  [warning]•[/warning] {conflict} (x{count})')
    console.print(f'[accent]claude-batch:[/accent] wrote {written} {config.tags_filename} file(s), '
                  f'{len(failures)} failure(s), {sum(conflicts.values())} facet correction(s)')
    console.print('[muted]Run [accent]update-tags[/accent] to reconcile before the next wave.[/muted]')
    return ExitCodes.EXIT_ERROR if failures else ExitCodes.EXIT_OK
