#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""File download and caching utilities for Project Euler solver."""
from __future__ import annotations

from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from uuid import NAMESPACE_URL, uuid5

from requests import get

from solver.workspace import cache_dir, write_file


# ============================================================================
# Download Functions
# ============================================================================

def download_file(url: str, *,
                  refresh: bool = False,
                  check_last_modified: bool = False,
                  verbose: bool = False) -> bytes | None:
    """Download a file from URL with caching support.

    Args:
        url: URL to download from
        refresh: Force re-download even if cached
        check_last_modified: Check if a cached file is outdated using Last-Modified header
        verbose: Print verbose output

    Returns:
        File content as bytes or None if download fails
    """
    cache_path = cache_dir / uuid5(NAMESPACE_URL, url).hex
    if not cache_path.exists():
        verbose and print(f'Info: {cache_path.name} not found for {url}, refreshing...')
        refresh = True
    elif check_last_modified and (modified := get(url, stream=True).headers.get('Last-Modified')):
        modified_dt = parsedate_to_datetime(modified)
        cached_dt = datetime.fromtimestamp(cache_path.stat().st_mtime, tz=timezone.utc)
        if modified_dt > cached_dt:
            verbose and print(f'Info: {cache_path.name} is out of date for {url}, refreshing...')
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
            write_file(cache_path, content)
            verbose and print(f'Downloaded {cache_path.name} from {url}')
    try:
        return cache_path.read_bytes()
    except Exception as e:
        print(f'Error: failed to read cache file {cache_path.name} for {url}: {e}')
        return None
    finally:
        verbose and print(f'Read {len(cache_path.read_bytes())} bytes for {url} from cache {cache_path.name}')
