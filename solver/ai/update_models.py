#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The `update-models` command: refresh the `Model` enum and its pricing.

The set of available Claude models and their per-token prices are moving targets. Rather
than hand-edit them on every model launch or price change, this command regenerates them
from live sources:

* the Anthropic Models API (`client.models.list()`) — the authoritative list of callable
  model IDs and their display names; and
* the public pricing page (`platform.claude.com/.../pricing.md`) — scraped for each model's
  base input and output price per million tokens (the Models API does not expose pricing).

In `models.py`, only the block between the `# GEN:models` / `# /GEN:models` markers is
rewritten — the enum members, their inline comments, and the `price` map. Curated per-model
comments are preserved across regenerations; a newly discovered model is commented with its
display name. Everything outside the markers is left untouched.

The USD→EUR rate `costs` converts with is *not* here: it is one setting refreshed by
:mod:`solver.ai.update_usd_rate`, a maintainer command. It was split out because it is a
different job at a different rung, and because a rate that drifts daily made `--check` below
report stale on almost every run.

The header's date stamp had crept back into the same trap from the other side: rendered as
*today* and compared, it made the block differ from itself on any day it had not already
been regenerated. It now records when the catalogue last **changed**, and a comparison
ignores it (:func:`_undated`), so a release no longer carries a commit that moved a date and
nothing else.

Exposed as the `update-models` shell command: `solver "update-models"` to rewrite,
`solver "update-models --check"` to verify (exit 1 if the block is out of date, writing
nothing).
"""
from __future__ import annotations

__all__ = ['update_models']

import re
from datetime import date
from pathlib import Path

from solver.config import ExitCodes, config
from solver.core.download import download_file
from solver.core.git import commit_regenerated
from solver.shell import console, register
from solver.utils.quips import quips

#: The module whose `Model` class this command maintains.
MODELS_FILE: Path = Path(__file__).resolve().with_name('models.py')


def _written() -> str:
    """This command's one output, as the repo-relative path its commit names."""
    return MODELS_FILE.relative_to(config.root_dir).as_posix()


#: The public pricing page scraped for per-token prices (the Models API exposes none).
PRICING_URL = 'https://platform.claude.com/docs/en/about-claude/pricing.md'

#: Matches the regenerated block: `# GEN:models …\n … \n# /GEN:models`.
_BLOCK_RE = re.compile(r'(# GEN:models\b[^\n]*\n).*?(# /GEN:models)', re.DOTALL)

#: Matches an existing enum member line: `NAME = 'model-id'  # comment`.
_MEMBER_RE = re.compile(r"^\s*[A-Z0-9_]+\s*=\s*'([^']+)'\s*#\s*(.*?)\s*$", re.MULTILINE)

#: Matches a dollar amount like `$10`, `$12.50`, `$0.50` in a pricing cell.
_PRICE_RE = re.compile(r'\$\s*([\d.]+)')

#: A trailing dated-snapshot suffix (`-20251001`) normalised back to the alias form.
_SNAPSHOT_RE = re.compile(r'-\d{8}$')

#: The header's date stamp, so a comparison can ignore it. See :func:`_undated`.
_DATED_RE = re.compile(r'\(last changed [^;]*;')


def _ordinal(day: int) -> str:
    """`1` → `1st`, `2` → `2nd`, `18` → `18th`, `23` → `23rd`."""
    if 11 <= day % 100 <= 13:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
    return f'{day}{suffix}'


def _today() -> str:
    """Today rendered as e.g. `18th June 2026`."""
    today = date.today()
    return f'{_ordinal(today.day)} {today:%B %Y}'


def _undated(text: str) -> str:
    """*text* with the header's date neutralised, for asking whether anything **else** moved.

    The date is the one part of the block that changes without the catalogue changing, so
    comparing it would make every run a rewrite: the block would be "out of date" on any day
    it had not already been regenerated, `--check` would fail daily, and a release would
    carry a commit that moved a date and nothing else. That is the same trap
    `update-usd-rate` was split out of this command to escape, arriving by another door.
    """
    return _DATED_RE.sub('(last changed …;', text)


def _enum_name(model_id: str) -> str:
    """Derive the enum member name from a model ID: `claude-opus-4-8` → `CLAUDE_OPUS_4_8`."""
    return re.sub(r'[-.]', '_', model_id).upper()


def _row_cells(line: str) -> list[str]:
    """Split a markdown table row into trimmed cells."""
    return [c.strip() for c in line.strip().strip('|').split('|')]


def _parse_pricing(markdown: str) -> dict[str, tuple[float, float]]:
    """Parse the `## Model pricing` table → `{display_name: (input, output)}` per MTok.

    Reads the first table whose header carries both `Base Input Tokens` and `Output Tokens`.
    The model column is the display name (e.g. `Claude Opus 4.8`), with any trailing
    `([deprecated]…)` / `([limited availability]…)` annotation stripped. Rows annotated
    `deprecated` or `retired` are skipped, so the enum tracks only current models.
    """
    lines = markdown.splitlines()
    prices: dict[str, tuple[float, float]] = {}
    for i, line in enumerate(lines):
        if not (line.lstrip().startswith('|') and 'Base Input Tokens' in line and 'Output Tokens' in line):
            continue
        header = _row_cells(line)
        in_idx, out_idx = header.index('Base Input Tokens'), header.index('Output Tokens')
        for row in lines[i + 2:]:  # skip the `|---|` separator row
            if not row.lstrip().startswith('|'):
                break
            cells = _row_cells(row)
            if len(cells) <= max(in_idx, out_idx) or re.search(r'deprecated|retired', cells[0], re.IGNORECASE):
                continue
            name = re.split(r'\s*[(\[]', cells[0], maxsplit=1)[0].strip()
            in_match, out_match = _PRICE_RE.search(cells[in_idx]), _PRICE_RE.search(cells[out_idx])
            if name and in_match and out_match:
                prices[name] = (float(in_match.group(1)), float(out_match.group(1)))
        break
    return prices


def _fetch_models() -> list[tuple[str, str]] | None:
    """Return `(model_id, display_name)` for every Claude model the API lists, or None on failure.

    Dated snapshot IDs (`claude-haiku-4-5-20251001`) are normalised to their alias
    (`claude-haiku-4-5`) so the enum member names stay stable across regenerations.
    """
    try:  # `anthropic` ships with the optional `ai` group; imported on demand
        import anthropic
    except ImportError:
        console.print('[error]update-models needs the [accent]ai[/accent] dependency group '
                      '— run [accent]pip install -e ".\\[ai]"[/accent].[/error]')
        return None
    from solver.ai.models import get_api_key
    try:
        client = anthropic.Anthropic(api_key=get_api_key())
        seen: dict[str, str] = {}
        for model in client.models.list():
            if model.id.startswith('claude-'):
                seen.setdefault(_SNAPSHOT_RE.sub('', model.id), model.display_name)
        return list(seen.items())
    except Exception as exc:
        console.print(f'[error]error:[/error] failed to list models from the Anthropic API: {exc}')
        return None


def _existing_comments() -> dict[str, str]:
    """Map each model ID currently in `models.py` to its inline comment (for preservation)."""
    text = MODELS_FILE.read_text()
    region = match.group(0) if (match := _BLOCK_RE.search(text)) else text
    return {model_id: comment for model_id, comment in _MEMBER_RE.findall(region)}


def _collect() -> list[tuple[str, str, float, float]] | None:
    """Join the API model list with scraped prices, sorted by price (then ID) descending.

    Returns `(model_id, display_name, input_price, output_price)` rows, or None if either
    source could not be reached. Models with no matching price on the docs page are skipped.
    """
    if (fetched := _fetch_models()) is None:
        return None
    raw: bytes = download_file(PRICING_URL, refresh=True)
    prices = _parse_pricing(raw.decode('utf-8'))
    models: list[tuple[str, str, float, float]] = []
    for model_id, display in fetched:
        if (price := prices.get(display)) is None:  # deprecated/retired, or not on the pricing page
            console.print(f'[muted]skipping [accent]{display}[/accent] ({model_id}) — no current price[/muted]')
            continue
        models.append((model_id, display, price[0], price[1]))
    models.sort(key=lambda m: m[0], reverse=True)  # ID descending (newest snapshot first)
    models.sort(key=lambda m: (m[2], m[3]), reverse=True)  # then by input, output price descending
    return models


def _render(models: list[tuple[str, str, float, float]], comments: dict[str, str]) -> str:
    """Render the `Model` class body (without the surrounding markers) from the collected models."""
    members = [
        f"    {_enum_name(model_id)} = '{model_id}'  # {comments.get(model_id, display)}"
        for model_id, display, _inp, _out in models
    ]
    price_rows = [
        f'            Model.{_enum_name(model_id)}: Price(input={inp:.2f}, output={out:.2f}),'
        for model_id, _display, inp, out in models
    ]
    return '\n'.join([
        f'class Model(StrEnum):  # Available models (last changed {_today()}; '
        f'pricing from platform.claude.com)',
        *members,
        '',
        '    @property',
        '    def price(self) -> Price:  # Cost in USD per million tokens, scraped from the pricing page',
        '        return {',
        *price_rows,
        '        }[self]',
    ])


# Admin: this command **generates package source**. It rewrites `solver/ai/models.py`, a
# tracked module every AI command then imports — the same kind of write that floors
# `update-docs` at admin, and a different act from curating data. `update-usd-rate`, which
# writes one managed setting and no code, is the maintainer half of what this used to be.
#
# The floor is not a promise the write will land. In a deployed instance the package tree is
# root-owned, so this completes in a developer checkout and fails on the filesystem anywhere
# else — a property of where it is run, not of who runs it, and one no floor can express.
# Egress is the other half: the Models API and the pricing page are allowlisted in
# scripts/setup/egress.sh.
@register(requires='admin', quietable=True)
def update_models(check: bool = False) -> int:
    """Refresh the model catalogue and its pricing.

    Lists the available Claude models from the Anthropic Models API, scrapes each model's base
    input/output price (per million tokens) from the public pricing page, and rewrites the
    `# GEN:models` block in `models.py` — the enum members, their inline comments, and the
    `price` map. Curated per-model comments are kept; a newly discovered model is commented
    with its display name. Nothing outside the markers is touched, and the USD→EUR rate is
    `update-usd-rate`'s to refresh.

    The header's date says when the catalogue last **changed**, not when it was last looked
    at: a run that finds nothing new writes nothing, so `--check` passes on any day the
    models and their prices have not moved.

    A regenerated block is committed, staging `models.py` and nothing beside it.

    Args:
        check: Write nothing and fail if the generated block is out of date. Defaults to
            False, which rewrites it in place.
    """
    if (models := _collect()) is None:
        return ExitCodes.EXIT_ERROR

    original = MODELS_FILE.read_text()
    if not _BLOCK_RE.search(original):
        console.print('[error]error:[/error] could not find the [accent]# GEN:models[/accent] markers in models.py')
        return ExitCodes.EXIT_ERROR
    body = _render(models, _existing_comments())
    rendered = _BLOCK_RE.sub(lambda m: f'{m.group(1)}{body}\n{m.group(2)}', original)
    if _undated(rendered) == _undated(original):
        # Nothing but the date differs, so nothing is written: the date says when the
        # catalogue last *moved*, which is what a reader of a price table wants to know.
        if check:
            console.print('[success]models are up to date[/success]')
            return ExitCodes.EXIT_OK
        console.print('[muted]models already up to date[/muted]')
        # Still offered to the committer: an earlier run may have written the block and failed
        # to commit it, and "up to date" must not mean "left dirty forever". Clean is a no-op.
        # This verb's whole output is the one file, so naming it is naming everything it writes.
        return commit_regenerated('update-models', quips['update-models'], [_written()])
    if check:
        console.print('[error]models out of date[/error] (run [accent]update-models[/accent]): '
                      '[warning]model pricing[/warning]')
        return ExitCodes.EXIT_ERROR

    MODELS_FILE.write_text(rendered)
    console.print(f'[success]updated[/success] {MODELS_FILE.relative_to(config.root_dir)} '
                  f'([accent]{len(models)}[/accent] models)')
    return commit_regenerated('update-models', quips['update-models'], [_written()],
                              [f'{model_id}: ${inp:.2f} in / ${out:.2f} out per MTok'
                               for model_id, _display, inp, out in models])
