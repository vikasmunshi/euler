#!/usr/bin/env python3
"""
Cached file downloader module.

This module provides functionality to download files from URLs with caching support.
Downloaded files are stored in a local cache directory using UUID-based filenames
derived from the URL. Subsequent requests for the same URL will use the cached
version unless a force refresh is requested.
"""
from pathlib import Path
from uuid import uuid5, NAMESPACE_URL

from requests import get


def download_file(url: str, force_refresh: bool = False) -> str:
    """Download a file from the given URL and return its contents as a string.

    Args:
        url (str): The URL of the file to download
        force_refresh (bool): If True, bypass the cache and re-download the file. Defaults to False.

    Returns:
        str: The contents of the downloaded file as text.
    """
    cache_dir = Path.cwd() / 'cache'
    url_uuid = uuid5(NAMESPACE_URL, url)
    cache_path = cache_dir / url_uuid.hex
    cache_path.parent.mkdir(parents=True, exist_ok=True)

    if force_refresh or not cache_path.exists():
        response = get(url, stream=True)
        with open(cache_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

    return cache_path.read_text()
