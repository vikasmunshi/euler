#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Wrapper for requests to cache files locally."""
from __future__ import annotations

import fcntl
import hashlib
from pathlib import Path

import requests

from euler_solver.framework.logger import logger
from euler_solver.framework.paths import base_dir


def url_cached_path(url: str) -> Path:
    cache_dir: Path = base_dir / 'resources' / 'data'
    cache_file: Path = cache_dir / hashlib.sha256(url.encode()).hexdigest()
    return cache_file


def get_text_file(url: str, force_refresh: bool = False) -> str:
    """
    Fetches the content of a text file from a given URL with caching enabled. The function utilizes
    a local cache to avoid redundant network requests and stores the cached files in a designated
    hidden directory. If the file is already present in the cache, it retrieves and returns the
    content. If not, it fetches the file from the URL, caches it locally, and then returns the
    content. The caching mechanism ensures concurrent process safety with file locks.

    Parameters:
        url (str): The URL of the text file to be fetched.
        force_refresh (bool, optional): If True, forces a refresh of the file from the URL. Defaults to False.

    Returns:
        str: The content of the text file.

    Exceptions:
        Requests' exceptions or IOError may propagate if issues occur during fetching or writing.
    """
    cache_file = url_cached_path(url=url)
    use_cache: bool = not force_refresh

    # Check if the file is already cached
    if use_cache and cache_file.exists():
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
    except requests.RequestException as e:
        logger.error(f"Error fetching URL {url}: {e}")
        raise
    except (IOError, OSError) as e:
        logger.error(f"Error accessing cache file {cache_file}: {e}")
        raise
