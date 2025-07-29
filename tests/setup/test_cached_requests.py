#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for the cached_requests module."""
import fcntl
import unittest
from pathlib import Path
from unittest.mock import mock_open, patch

from requests import RequestException

from euler.logger import logger
from euler.setup.base_dir import base_dir
from euler.setup.cached_requests import get_text_file, url_cached_path

logger.setLevel('CRITICAL')

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


class TestCachedRequestsMocked(unittest.TestCase):
    """Test cases for the cached_requests module utilizing pathlib.Path and requests.get."""

    @patch('fcntl.flock')
    @patch('requests.get')
    @patch('builtins.open', new_callable=mock_open, read_data='mocked file content')
    @patch('pathlib.Path.exists')
    def test_get_text_file_from_cache(self, mock_exists, mock_file_open, mock_requests, mock_flock):
        """Test that get_text_file retrieves content from the cache."""
        url = "https://example.com/mock-data.txt"
        cache_file = Path("/mocked/cache/path/mock-data.txt")

        # Simulate that the file exists in the cache
        mock_exists.return_value = True

        # Mock the file descriptor to ensure compatibility with fcntl
        mock_file = mock_file_open.return_value
        mock_file.fileno.return_value = 10  # Mock a valid file descriptor

        # Patch url_cached_path to return the mocked cache file path
        with patch('euler.setup.cached_requests.url_cached_path', return_value=cache_file):
            content = get_text_file(url)

        # Verify the file was opened and no network requests were made
        mock_file_open.assert_called_once_with(cache_file, 'r')
        self.assertEqual(mock_file.fileno.call_count, 2)  # Ensure fileno() was called twice
        mock_requests.assert_not_called()
        mock_flock.assert_any_call(10, fcntl.LOCK_SH)  # Ensure fcntl.flock was called with LOCK_SH
        mock_flock.assert_any_call(10, fcntl.LOCK_UN)  # Ensure fcntl.flock was called with LOCK_UN
        self.assertEqual(content, 'mocked file content')

    @patch('fcntl.flock')
    @patch('requests.get')
    @patch('builtins.open', new_callable=mock_open)
    @patch('pathlib.Path.exists')
    def test_get_text_file_from_url(self, mock_exists, mock_file_open, mock_requests, mock_flock):
        """Test that get_text_file fetches content from the URL and caches it."""
        url = "https://example.com/mock-data.txt"
        cache_file = Path("/mocked/cache/path/mock-data.txt")
        mock_response_content = "mocked network content"

        # Simulate that the file does not exist in the cache
        mock_exists.return_value = False

        # Mock the requests.get response
        mock_requests.return_value.status_code = 200
        mock_requests.return_value.text = mock_response_content

        # Mock the file write operations
        mock_file = mock_file_open.return_value

        # Patch url_cached_path to return the mocked cache file path
        with patch('euler.setup.cached_requests.url_cached_path', return_value=cache_file):
            content = get_text_file(url)

        # Verify the content was fetched from the network
        mock_requests.assert_called_once_with(url, timeout=10)

        # Verify the content was written to the cache
        mock_file_open.assert_called_once_with(cache_file, 'w')  # File opened in write mode
        mock_file.write.assert_called_once_with(mock_response_content)  # Content written to the file

        # Verify that fcntl was used for locking the file
        mock_flock.assert_any_call(mock_file.fileno(), fcntl.LOCK_EX)  # Lock for writing
        mock_flock.assert_any_call(mock_file.fileno(), fcntl.LOCK_UN)  # Unlock after writing

        # Ensure the correct content was returned
        self.assertEqual(content, mock_response_content)

    @patch('fcntl.flock')
    @patch('requests.get')
    @patch('builtins.open', new_callable=mock_open, read_data='mocked file content')
    @patch('pathlib.Path.exists')
    def test_get_text_file_handles_network_error(self, mock_exists, mock_file_open, mock_requests, mock_flock):
        """Test that get_text_file raises a RequestException when a network error occurs."""
        logger.setLevel('CRITICAL')
        url = "https://example.com/mock-data.txt"

        # Simulate the cache directory and file
        cache_dir = Path("/mocked/cache/path")
        cache_file = cache_dir / "mock-data.txt"

        # Simulate that the file does not exist in the cache
        mock_exists.return_value = False

        # Simulate a network error by raising a RequestException
        mock_requests.side_effect = RequestException("Network error!")

        def mock_url_cached_path(url: str) -> Path:
            return cache_file

        # Patch url_cached_path to use the mock implementation
        with patch('euler.setup.cached_requests.url_cached_path', side_effect=mock_url_cached_path):
            with self.assertRaises(RequestException) as context:
                get_text_file(url)

        # Verify the exception message
        self.assertEqual(str(context.exception), "Network error!")

        # Ensure that the cache file was opened in write mode before the exception occurred
        mock_file_open.assert_called_once_with(cache_file, 'w')

    @patch('fcntl.flock')
    @patch('requests.get')
    @patch('builtins.open', new_callable=mock_open)  # Mock regular Python `open` for testing file access
    @patch('pathlib.Path.exists')
    def test_get_text_file_handles_cache_access_error(self, mock_exists, mock_file_open, mock_requests, mock_flock):
        """Test that get_text_file handles cache file access error."""
        logger.setLevel('CRITICAL')
        url = "https://example.com/mock-data.txt"
        cache_file = Path("/mocked/cache/path/mock-data.txt")

        # Simulate that the file exists in the cache
        mock_exists.return_value = False

        # Simulate an IOError when trying to access the cache file
        mock_file_open.side_effect = IOError("Cache access error!")

        # Patch url_cached_path to return the mocked cache file path
        with patch('euler.setup.cached_requests.url_cached_path', return_value=cache_file):
            with self.assertRaises(IOError) as context:
                get_text_file(url)

        # Verify that the raised exception message matches the expected error
        self.assertEqual(str(context.exception), "Cache access error!")

        # Ensure that the requests.get was never called because caching logic fails early
        mock_requests.assert_not_called()

    def test_get_base_dir(self):
        """Test that get_base_dir returns the correct package root directory."""
        package_name = 'euler'
        self.assertEqual(base_dir.name, package_name)
        self.assertTrue(base_dir.is_dir())


if __name__ == '__main__':
    unittest.main()
