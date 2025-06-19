#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
from functools import lru_cache


def parse_html_tags(text: str) -> str:
    """Parse HTML tags and convert special characters to their text representation.

    Handles both standard HTML entities and LaTeX-style math notation that appears
    in Project Euler problems.

    Args:
        text: HTML text to parse

    Returns:
        Text with HTML tags removed and special characters converted
    """
    # Replace <br> tags with newlines
    text = re.sub(r'<br\s*/?>', '\n', text)

    # Remove <p> and </p> tags
    text = re.sub(r'</?p>', '', text)

    # Convert common HTML entities
    html_entities = {
        '&lt;': '<',
        '&gt;': '>',
        '&amp;': '&',
        '&quot;': '"',
        '&apos;': "'",
        '&nbsp;': ' ',
        '&mdash;': '—',
        '&ndash;': '–',
        '&hellip;': '…',
        '&ldquo;': '"',
        '&rdquo;': '"',
        '&lsquo;': "'",
        '&rsquo;': "'"
    }

    # Replace HTML entities
    for entity, replacement in html_entities.items():
        text = text.replace(entity, replacement)

    # Handle numeric HTML entities (like &#39; for apostrophe)
    text = re.sub(r'&#(\d+);', lambda match: chr(int(match.group(1))), text)

    # Handle LaTeX-style math notation
    # Convert \dots to ...
    text = text.replace('\\dots', '...')

    # Preserve $ for math notation
    # (Project Euler problems use $ and $$ for LaTeX math notation)

    # Remove other HTML tags
    text = re.sub(r'<[^>]*>', '', text)

    return text


@lru_cache(maxsize=None)
def word_to_number(word: str) -> int:
    """Convert a word to a number by summing the alphabetical position values of each letter.

    Each letter is assigned a value based on its position in the alphabet (A=1, B=2, etc.).
    Used in Project Euler problems where alphabetical values of words are needed.

    Args:
        word: The input word (expected to be uppercase letters)

    Returns:
        The sum of the alphabetical positions of all letters in the word
    """
    return sum(ord(c) - 64 for c in word)
