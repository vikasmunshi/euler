#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Available models and their pricing, plus a utility function to calculate costs. """
from __future__ import annotations

from enum import StrEnum
from functools import lru_cache
from typing import Any, Literal, NamedTuple

from dotenv import dotenv_values

from solver.config import config
from solver.shell import register


class Model(StrEnum):  # Available models (as of May 2026)
    CLAUDE_OPUS_4_6 = 'claude-opus-4-6'  # most intelligent; best for hard reasoning, agents, coding
    CLAUDE_SONNET_4_6 = 'claude-sonnet-4-6'  # best speed/intelligence balance; good for structured generation
    CLAUDE_HAIKU_4_5 = 'claude-haiku-4-5'  # fastest and cheapest; simple/high-volume tasks only

    @property
    def price(self) -> Price:  # Cost in USD per million tokens, as of May 2026
        return {
            Model.CLAUDE_OPUS_4_6: Price(input=15.00, output=75.00),
            Model.CLAUDE_SONNET_4_6: Price(input=3.00, output=15.00),
            Model.CLAUDE_HAIKU_4_5: Price(input=0.80, output=4.00),
        }[self]


class Price(NamedTuple):
    input: float
    output: float

    #: Cache writes (cache_creation_input_tokens) are billed at 1.25x the input rate;
    #: cache reads (cache_read_input_tokens) are billed at 0.10x the input rate.
    @property
    def cache_write(self) -> float:
        return self.input * 1.25

    @property
    def cache_read(self) -> float:
        return self.input * 0.10

    def cost(self, *,
             input_tokens: int,
             output_tokens: int,
             cache_creation_tokens: int = 0,
             cache_read_tokens: int = 0) -> float:
        return (self.input * input_tokens
                + self.cache_write * cache_creation_tokens
                + self.cache_read * cache_read_tokens
                + self.output * output_tokens) / 1_000_000


TokenKind = Literal['input', 'output', 'cache_creation', 'cache_read']

consumed_tokens: dict[Model, dict[TokenKind, int]] = {
    model: {'input': 0, 'output': 0, 'cache_creation': 0, 'cache_read': 0}
    for model in Model
}


def record_usage(model: Model, usage: Any) -> None:
    """Record token counts from an Anthropic 'response.usage' into 'consumed_tokens'.

    Tolerates older SDKs that may not expose cache-token attributes by treating missing
    or 'None' fields as zero.
    """
    bucket = consumed_tokens[model]
    bucket['input'] += int(getattr(usage, 'input_tokens', 0) or 0)
    bucket['output'] += int(getattr(usage, 'output_tokens', 0) or 0)
    bucket['cache_creation'] += int(getattr(usage, 'cache_creation_input_tokens', 0) or 0)
    bucket['cache_read'] += int(getattr(usage, 'cache_read_input_tokens', 0) or 0)


def get_accumulated_charges() -> float:
    """Return the total accumulated charges for all models in the session."""
    return sum(model.price.cost(input_tokens=consumed_tokens[model]['input'],
                                output_tokens=consumed_tokens[model]['output'],
                                cache_creation_tokens=consumed_tokens[model]['cache_creation'],
                                cache_read_tokens=consumed_tokens[model]['cache_read'])
               for model in consumed_tokens)


@register(name='costs',
          help='Calculate and display the total cost of AI tokens consumed in the session.',
          usage='costs [usd_to_eur=<config.usd_to_eur>]', )
def costs(usd_to_eur: float | None = None) -> str:
    """
    Return a formatted cost string for all AI tokens consumed in the session so far, or "nil"
    if nothing has been consumed.

    Totals the charges across all models in "consumed_tokens" using each model's published USD
    price per million tokens (with cache writes at 1.25x and cache reads at 0.10x the input rate),
    then converts to EUR using "usd_to_eur".

    Args:
        usd_to_eur: USD-to-EUR conversion rate (euros per dollar). Defaults to 'config.usd_to_eur'.
    """
    rate: float = config.usd_to_eur if usd_to_eur is None else usd_to_eur
    charges_usd: float = get_accumulated_charges()
    if charges_usd == 0.0:
        return 'nil'
    charges_eur: float = charges_usd * rate
    parts: list[str] = []
    for model, b in consumed_tokens.items():
        if any(b.values()):
            parts.append(f'{model}: input {b["input"]}, output {b["output"]}, '
                         f'cache_write {b["cache_creation"]}, cache_read {b["cache_read"]}')
    return f'${charges_usd:.4f} (€{charges_eur:.4f} at {rate:.2f} $/€) [{"; ".join(parts)}]'


@lru_cache(maxsize=None)
def get_api_key() -> str:
    """Read 'ANTHROPIC_API_KEY' from the project's '.env' file.

    Delegates to 'python-dotenv' ('ai' extra), which handles the full dotenv grammar:
    'export' prefix, single/double-quoted values, inline '#' comments, escape sequences,
    multi-line quoted values, and variable interpolation.
    """
    name = 'ANTHROPIC_API_KEY'
    env_file = config.root_dir / '.env'
    value = dotenv_values(env_file).get(name)
    if not value:
        raise ValueError(f'{name} not found in .env file, please set it to your Anthropic API key')
    return value


__all__ = ('Model', 'Price', 'TokenKind', 'costs', 'get_accumulated_charges', 'get_api_key', 'record_usage')
