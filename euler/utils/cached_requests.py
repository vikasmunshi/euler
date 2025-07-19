#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import fcntl
import hashlib
from pathlib import Path

import requests

from euler.logger import logger


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
    cache_dir = Path(__file__).parent.parent / 'resources/data'
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
