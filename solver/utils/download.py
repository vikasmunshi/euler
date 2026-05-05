#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""URL file download with local caching and optional refresh."""
from __future__ import annotations

from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from uuid import NAMESPACE_URL, uuid5

from requests import get

from solver.config import cache_dir
from solver.utils.utils import write_file


def download_file(url: str, *,
                  refresh: bool = False,
                  check_last_modified: bool = False,
                  verbose: bool = False) -> bytes | None:
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
        verbose:             If True, print progress messages for cache misses, refreshes, and reads.
                             Defaults to False.

    Returns:
        The file contents as bytes, or None if the download or cache read fails.
    """
    cache_path = cache_dir / uuid5(NAMESPACE_URL, url).hex
    if not cache_path.exists():
        if verbose:
            print(f'Info: {cache_path.name} not found for {url}, refreshing...')
        refresh = True
    elif check_last_modified and (modified := get(url, stream=True).headers.get('Last-Modified')):
        modified_dt = parsedate_to_datetime(modified)
        cached_dt = datetime.fromtimestamp(cache_path.stat().st_mtime, tz=timezone.utc)
        if modified_dt > cached_dt:
            if verbose:
                print(f'Info: {cache_path.name} is out of date for {url}, refreshing...')
            refresh = True
    if refresh:
        try:
            response = get(url, stream=True)
            response.raise_for_status()
            content: bytes = b''.join(chunk for chunk in response.iter_content(chunk_size=8192))
        except Exception as e:
            print(f'Error: failed to download {cache_path.name} from {url}: {e}')
            return None
        else:
            write_file(cache_path, content, msg=f'Downloaded from {url}' if verbose else None)
    try:
        return cache_path.read_bytes()
    except Exception as e:
        print(f'Error: failed to read cache file {cache_path.name} for {url}: {e}')
        return None
    finally:
        if verbose:
            print(f'Read {len(cache_path.read_bytes())} bytes for {url} from cache {cache_path.name}')


__all__ = ('download_file',)
