#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for the cached_requests module."""
import os
import unittest

from euler.logger import logger
from euler.utils.cached_requests import get_text_file, url_cached_path

logger.setLevel('ERROR')

# Dictionary of test URLs mapped to their expected content (first 10 characters)
test_urls_with_10_chars = {
    'https://projecteuler.net/resources/documents/0022_names.txt': '"MARY","PATRICIA","LINDA",',
    'https://projecteuler.net/resources/documents/0054_poker.txt': '8C TS KC 9H 4S 7D 2S 5D 3S AC',
    'https://projecteuler.net/resources/documents/0059_cipher.txt': '36,22,80,0,0,4,23,25,19,17,88',
    'https://projecteuler.net/resources/documents/0067_triangle.txt': '59\n',
    'https://projecteuler.net/resources/documents/0079_keylog.txt': '319\n',
    'https://projecteuler.net/resources/documents/0081_matrix.txt': '4445,2697,5115,718,2209,2212,654,4348,',
    'https://projecteuler.net/resources/documents/0082_matrix.txt': '4445,2697,5115,718,2209,2212,654,4348,',
    'https://projecteuler.net/resources/documents/0083_matrix.txt': '4445,2697,5115,718,2209,2212,654,4348,',
    'https://projecteuler.net/resources/documents/0089_roman.txt': 'MMMMDCLXXII',
    'https://projecteuler.net/project/resources/p096_sudoku.txt': 'Grid 01\n003020600',
    'https://projecteuler.net/resources/documents/0098_words.txt': '"A","ABILITY","ABLE","ABOUT","ABOVE",',
    'https://projecteuler.net/resources/documents/0099_base_exp.txt': '519432,525806',
}


class TestCachedRequests(unittest.TestCase):
    """Test cases for the cached_requests module."""

    def test_get_text_file_from_cache(self):
        """Test fetching a text file from a URL and caching it."""
        for url, sample in test_urls_with_10_chars.items():
            cache_file = url_cached_path(url)
            content = get_text_file(url)
            self.assertTrue(cache_file.is_file())
            self.assertTrue(content.startswith(sample))

    def test_get_text_file_from_url(self):
        if not os.getenv('TEST_NETWORK'):
            self.skipTest('Skipping network tests')
        else:
            url, sample = list(test_urls_with_10_chars.items())[2]
            cache_file = url_cached_path(url)
            if cache_file.exists():
                cache_file.unlink()
            content = get_text_file(url)
            self.assertTrue(cache_file.exists())
            self.assertTrue(cache_file.is_file())
            self.assertTrue(content.startswith(sample))


if __name__ == '__main__':
    unittest.main()
