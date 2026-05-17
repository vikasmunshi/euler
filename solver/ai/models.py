#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Available models and their pricing, plus a utility function to calculate costs. """
from __future__ import annotations

from enum import StrEnum
from functools import lru_cache
from typing import Literal, NamedTuple

from solver.core.config import Config


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

    def cost(self, input_tokens: int, output_tokens: int) -> float:
        return (self.input * input_tokens + self.output * output_tokens) / 1_000_000


consumed_tokens: dict[Model, dict[Literal['input', 'output'], int]] = {
    Model.CLAUDE_OPUS_4_6: {'input': 0, 'output': 0},
    Model.CLAUDE_SONNET_4_6: {'input': 0, 'output': 0},
    Model.CLAUDE_HAIKU_4_5: {'input': 0, 'output': 0},
}


def costs(usd_to_eur: float = 0.92) -> str:  # Conversion rate as of May 2026
    """
    Return a formatted cost string for all AI tokens consumed in the session so far,
    or None if nothing has been consumed.

    Totals the charges across all models in "consumed_tokens" using each model's published USD
    price per million tokens, then converts to EUR using "usd_to_eur".

    Args:
        usd_to_eur: USD-to-EUR conversion rate (dollars per euro).  Defaults to 0.92 (May 2026).

    Returns:
        A string of the form "$0.0123 (€0.0113 at 0.92 $/€) [model_name: input 1000, output 500; ...]",
        where the bracketed section lists input and output token counts for each model that consumed tokens,
        or "nil" if no tokens have been consumed yet.
    """
    charges_usd: float = sum(model.price.cost(consumed_tokens[model]['input'], consumed_tokens[model]['output'])
                             for model in consumed_tokens)
    if charges_usd == 0.0:
        return 'nil'
    charges_eur: float = charges_usd * usd_to_eur
    consumed_tokens_str: str = '; '.join(f'{model}: input {input_tokens}, output {consumption['output']}'
                                         for model, consumption in consumed_tokens.items()
                                         if (input_tokens := consumption['input']))
    return f'${charges_usd:.4f} (€{charges_eur:.4f} at {usd_to_eur:.2f} $/€) [{consumed_tokens_str}]'


@lru_cache(maxsize=None)
def get_api_key() -> str:
    """Read ANTHROPIC_API_KEY from the project .env file."""
    env_file = Config.root_dir / '.env'
    for line in env_file.read_text().splitlines():
        if line.startswith('ANTHROPIC_API_KEY='):
            return line.split('=', 1)[1].strip()
    raise ValueError('ANTHROPIC_API_KEY not found in .env file, please set it to your Anthropic API key')


__all__ = ('Model', 'Price', 'consumed_tokens', 'costs', get_api_key())
