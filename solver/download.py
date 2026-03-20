#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
from __future__ import annotations

from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from uuid import NAMESPACE_URL, uuid5

from requests import get

from solver.workspace import CACHE_DIR, write_file


def download_file(url: str, *, refresh: bool = False, check_validity: bool = False) -> bytes | None:
    cache_path = CACHE_DIR / uuid5(NAMESPACE_URL, url).hex
    if not cache_path.exists():
        print(f'Info: {cache_path.name} not found for {url}, refreshing...')
        refresh = True
    elif check_validity and (modified := get(url, stream=True).headers.get('Last-Modified')):
        modified_dt = parsedate_to_datetime(modified)
        cached_dt = datetime.fromtimestamp(cache_path.stat().st_mtime, tz=timezone.utc)
        if modified_dt > cached_dt:
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
            write_file(cache_path, content)
            print(f'Downloaded {cache_path.name} from {url}')
    try:
        return cache_path.read_bytes()
    except Exception as e:
        print(f'Error: failed to read cache file {cache_path.name} for {url}: {e}')
        return None
    finally:
        print(f'Read {len(cache_path.read_bytes())} bytes for {url} from cache {cache_path.name}')
