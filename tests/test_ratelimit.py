#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Unit tests for solver.web.auth.ratelimit."""
from __future__ import annotations

import unittest
from unittest.mock import patch

from solver.web.auth.ratelimit import RateLimiter


class RateLimiterTests(unittest.TestCase):
    def test_allows_up_to_limit_then_blocks(self) -> None:
        limiter = RateLimiter(max_requests=3, window_seconds=60)
        self.assertTrue(all(limiter.allow('ip') for _ in range(3)))
        self.assertFalse(limiter.allow('ip'))          # 4th within the window is blocked

    def test_keys_are_independent(self) -> None:
        limiter = RateLimiter(max_requests=1, window_seconds=60)
        self.assertTrue(limiter.allow('a'))
        self.assertFalse(limiter.allow('a'))
        self.assertTrue(limiter.allow('b'))            # a different key has its own budget

    def test_window_slides(self) -> None:
        limiter = RateLimiter(max_requests=1, window_seconds=60)
        with patch('solver.web.auth.ratelimit.time.time', return_value=1000.0):
            self.assertTrue(limiter.allow('ip'))
            self.assertFalse(limiter.allow('ip'))
        with patch('solver.web.auth.ratelimit.time.time', return_value=1061.0):
            self.assertTrue(limiter.allow('ip'))       # earlier hit aged out of the window


if __name__ == '__main__':
    unittest.main()
