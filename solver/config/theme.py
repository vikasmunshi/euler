#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Dynamic configuration: how the shell **looks**.

The one palette, in two dialects — a `rich` theme for everything the console prints and a
`prompt_toolkit` style for the input line. Split out of :mod:`solver.config.settings` because
it is the only part of the configuration that needs those two libraries, and the static
half must stay importable by processes that have neither reason nor room for them (the git
filter, the web service tiers). :attr:`solver.config.Config.theme` and `.style` are
`cached_property`, so nothing here is imported until something actually renders.
"""
from __future__ import annotations

__all__ = ['console_style', 'console_theme']

from prompt_toolkit.styles import Style
from rich.theme import Theme


def console_theme() -> Theme:
    """The `rich` console theme: semantic names, resolved to the dark palette."""
    return Theme({
        'accent': 'bold #f97316',  # warm orange accent (Junie highlight)
        'accent.dim': '#c2410c',
        'primary': '#e5e7eb',  # near-white body text
        'muted': '#9ca3af',  # secondary / hints
        'success': 'bold #22c55e',
        'warning': 'bold #f59e0b',
        'error': 'bold #ef4444',
        'panel.border': '#3f3f46',
        'prompt.path': '#60a5fa',
        'prompt.symbol': 'bold #f97316',
        'cmd.name': 'bold #fbbf24',
        'cmd.help': '#9ca3af',
        # Markdown rendering (rich.markdown.Markdown) — keyed only by rich's Markdown
        # renderer; tuned to the dark theme so inline code etc. stay readable (no bg block).
        'markdown.code': 'bold #fbbf24',  # inline `code` — amber, no background
        'markdown.code_block': '#fbbf24',
        'markdown.item.bullet': 'bold #f97316',
        'markdown.h1': 'bold #f97316',
        'markdown.h2': 'bold #f97316',
        'markdown.h3': 'bold #fbbf24',
        'markdown.h4': 'bold #fbbf24',
        'markdown.link': '#60a5fa',
        'markdown.link_url': '#60a5fa',
    })


def console_style() -> Style:
    """The `prompt_toolkit` style for the input line."""
    return Style.from_dict({
        'prompt.bar': '#f97316 bold',
        'prompt.path': '#60a5fa',
        'prompt.symbol': '#f97316 bold',
        'prompt.user': '#e5e7eb',
        '': '#60a5fa',  # typed input text
        'auto-suggestion': '#9ca3af',  # muted light grey
        'bottom-toolbar': 'bg:#27272a #9ca3af',
    })
