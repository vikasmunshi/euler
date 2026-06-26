#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Utility for downloading and caching files via HTTP. """
from __future__ import annotations

__all__ = ['download_file']

from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from uuid import NAMESPACE_URL, uuid5

from requests import get

from solver.config import config


def download_file(
        url: str, *,
        refresh: bool = False,
        check_last_modified: bool = False,
) -> bytes:
    """
    Download a file from a URL, serving from a local cache when available.

    The cache key is a UUID5 derived from the URL, so each URL maps to a unique cache entry.
    A cached copy is used unless refresh is True, the cache entry is missing, or
    check_last_modified detects that the remote file is newer than the cached copy.

    Args:
        url:                 URL of the file to download.
        refresh:             If True, re-download and overwrite the cached copy. Defaults to False.
        check_last_modified: If True, send a HEAD request and compare the remote Last-Modified
                             header against the cache file's mtime; refresh if the remote is newer.
                             Defaults to False.

    Returns:
        The file contents as bytes
    """
    cache_path = config.cache_dir / uuid5(NAMESPACE_URL, url).hex
    if not cache_path.exists():
        refresh = True
    elif check_last_modified and (modified := get(url, stream=True).headers.get('Last-Modified')):
        modified_dt = parsedate_to_datetime(modified)
        cached_dt = datetime.fromtimestamp(cache_path.stat().st_mtime, tz=timezone.utc)
        if modified_dt > cached_dt:
            refresh = True
    if refresh:
        response = get(url, stream=True)
        response.raise_for_status()
        content: bytes = b''.join(chunk for chunk in response.iter_content(chunk_size=8192))
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_bytes(content)
    return cache_path.read_bytes()
