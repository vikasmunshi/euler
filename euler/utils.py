#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import fcntl
import hashlib
import re
from functools import lru_cache
from pathlib import Path

import requests

from euler.logger import logger


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
def word_to_num(word: str) -> int:
    """Convert a word to a number by summing the alphabetical position values of each letter.

    Each letter is assigned a value based on its position in the alphabet (A=1, B=2, etc.).
    Used in Project Euler problems where alphabetical values of words are needed.

    Args:
        word: The input word (expected to be uppercase letters)

    Returns:
        The sum of the alphabetical positions of all letters in the word
    """
    return sum(ord(c) - 64 for c in word.strip('"'))


def get_text_file(url: str) -> str:
    """
    Fetches the content of a text file from a given URL with caching enabled. The function utilizes
    a local cache to avoid redundant network requests and stores the cached files in a designated
    hidden directory. If the file is already present in the cache, it retrieves and returns the
    content. If not, it fetches the file from the URL, caches it locally, and then returns the
    content. The caching mechanism ensures concurrent process safety with file locks.

    Parameters:
        url (str): The URL of the text file to be fetched.

    Returns:
        str: The content of the text file.

    Exceptions:
        Requests' exceptions or IOError may propagate if issues occur during fetching or writing.
    """
    cache_dir = Path('.euler_cache')
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_file = cache_dir / hashlib.sha256(url.encode()).hexdigest()

    # Check if the file is already cached
    if cache_file.exists():
        with open(cache_file, 'r') as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            content = f.read()
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        logger.info({'action': 'retrieved_text_file_from_cache', 'url': url, 'content_length': len(content)})
        return content

    # If not cached, fetch and cache the file
    try:
        with open(cache_file, 'w') as lock_file:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            content = response.text
            lock_file.write(content)
            lock_file.flush()
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
        logger.info({'action': 'retrieved_text_file', 'url': url, 'content_length': len(content)})
        return content
    except (IOError, OSError) as e:
        logger.error(f"Error accessing cache file {cache_file}: {e}")
        raise
    except requests.RequestException as e:
        logger.error(f"Error fetching URL {url}: {e}")
        raise
