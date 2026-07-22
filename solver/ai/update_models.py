#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The `update-models` command: refresh the `Model` enum, pricing, and FX rate.

The set of available Claude models, their per-token prices, and the USD→EUR rate the `costs`
command uses are all moving targets. Rather than hand-edit them on every model launch, price
change, or currency drift, this command refreshes them from live sources:

* the Anthropic Models API (`client.models.list()`) — the authoritative list of callable
  model IDs and their display names;
* the public pricing page (`platform.claude.com/.../pricing.md`) — scraped for each model's
  base input and output price per million tokens (the Models API does not expose pricing); and
* the European Central Bank euro reference rates (`eurofxref-daily.xml`) — the authoritative,
  free, no-key source for the `ecb_usd_rate` rate in `config.json` (used only by `costs`).

In `models.py`, only the block between the `# GEN:models` / `# /GEN:models` markers is
rewritten — the enum members, their inline comments, and the `price` map. Curated per-model
comments are preserved across regenerations; a newly discovered model is commented with its
display name. Everything outside the markers is left untouched. The `ecb_usd_rate` rate is
written back through `config.dump_managed_config()`.

Exposed as the `update-models` shell command: `solver "update-models"` to rewrite,
`solver "update-models --check"` to verify (exit 1 if anything is out of date, writing
nothing). Note that the FX rate drifts daily, so `--check` will usually flag it as stale.
"""
from __future__ import annotations

__all__ = ['update_models']

import re
from datetime import date
from pathlib import Path

from solver.config import ExitCodes, config
from solver.core.download import download_file
from solver.shell import console, register

#: The module whose `Model` class this command maintains.
MODELS_FILE: Path = Path(__file__).resolve().with_name('models.py')

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

#: The ECB euro foreign-exchange reference rates (daily, free, no API key) — the authoritative
#: source for EUR conversions. It quotes `1 EUR = N USD`, so `ecb_usd_rate` is `N`.
ECB_FX_URL = 'https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml'

#: Matches the USD reference rate in the ECB feed: `<Cube currency='USD' rate='1.1591'/>`.
_USD_RATE_RE = re.compile(r"""currency=['"]USD['"]\s+rate=['"]([\d.]+)['"]""")


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


def _fetch_ecb_usd_rate() -> float | None:
    """Fetch the current USD→EUR rate (euros per dollar) from the ECB daily reference feed.

    The ECB quotes `1 EUR = N USD`
    Returns None if the feed is unreachable or carries no USD rate.
    """
    raw: bytes = download_file(ECB_FX_URL, refresh=True)
    if not (match := _USD_RATE_RE.search(raw.decode('utf-8'))):
        console.print(f'[error]error:[/error] no USD rate found in the ECB feed at {ECB_FX_URL}')
        return None
    return float(match.group(1))


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
        f'class Model(StrEnum):  # Available models (as of {_today()}; pricing from platform.claude.com)',
        *members,
        '',
        '    @property',
        '    def price(self) -> Price:  # Cost in USD per million tokens, scraped from the pricing page',
        '        return {',
        *price_rows,
        '        }[self]',
    ])


@register(requires='maintainer',
          help_text='Update Model enum, pricing, and USD→EUR rate.',
          quietable=True)
def update_models(check: bool = False) -> int:
    """Refresh the `Model` class in `models.py` and the `usd_to_eur` rate in `config.json`.

    Lists the available Claude models from the Anthropic Models API, scrapes each model's base
    input/output price (per million tokens) from the public pricing page, and rewrites the
    `# GEN:models` block in `models.py` — the enum members, their inline comments, and the
    `price` map. Curated per-model comments are kept; a newly discovered model is commented with
    its display name. Separately, fetches the USD→EUR rate from the ECB daily reference feed and
    writes it to `config.json` (the rate is used only by `costs`). Nothing else is touched.

    Args:
        check:  When True, write nothing and fail (non-zero) if either the model block or the
                FX rate is out of date. When False (default), rewrite both in place. The FX rate
                drifts daily, so `--check` will usually report it as stale.
    """
    if (models := _collect()) is None:
        return ExitCodes.EXIT_ERROR

    original = MODELS_FILE.read_text()
    if not _BLOCK_RE.search(original):
        console.print('[error]error:[/error] could not find the [accent]# GEN:models[/accent] markers in models.py')
        return ExitCodes.EXIT_ERROR
    body = _render(models, _existing_comments())
    rendered = _BLOCK_RE.sub(lambda m: f'{m.group(1)}{body}\n{m.group(2)}', original)
    models_stale = rendered != original

    rate = _fetch_ecb_usd_rate()  # None on fetch failure — leaves the existing rate untouched
    rate_stale = rate is not None and abs(rate - config.ecb_usd_rate) > 5e-5

    if not models_stale and not rate_stale:
        console.print('[muted]models and USD→EUR rate already up to date[/muted]')
        return ExitCodes.EXIT_OK
    if check:
        if models_stale:
            console.print('[error]models out of date[/error] (run [accent]update-models[/accent])')
        if rate_stale:
            console.print(f'[error]USD→EUR rate out of date[/error] '
                          f'([accent]{config.ecb_usd_rate} → {rate}[/accent])')
        return ExitCodes.EXIT_ERROR

    if models_stale:
        MODELS_FILE.write_text(rendered)
        console.print(f'[success]updated[/success] {MODELS_FILE.relative_to(config.root_dir)} '
                      f'([accent]{len(models)}[/accent] models)')
    if rate_stale and rate is not None:
        previous, config.ecb_usd_rate = config.ecb_usd_rate, rate
        config.dump_managed_config()
        console.print(f'[success]updated[/success] ecb_usd_rate in '
                      f'{config.managed_config_file.relative_to(config.root_dir)} '
                      f'([accent]{previous} → {rate}[/accent])')
    return ExitCodes.EXIT_OK
