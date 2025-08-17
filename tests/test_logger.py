#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for the logger module."""
import json
import logging
import sys
import unittest
from unittest.mock import MagicMock, patch

from euler_solver.logger import JsonFormatter, logger


class TestLogger(unittest.TestCase):
    def test_logger_is_configured(self):
        """Test that the logger is properly configured."""
        # Verify that the logger is an instance of `logging.Logger`
        self.assertIsInstance(logger, logging.Logger)

        self.assertEqual(logger.name, "euler_solver")

        # Verify that the logger has handlers attached
        self.assertTrue(logger.hasHandlers())

    @patch('logging.Logger.info')
    def test_logger_info_level(self, mock_info):
        """Test logging a message at the INFO level."""
        logger.info("This is an info message.")

        # Verify `logger.info` is called with the correct message
        mock_info.assert_called_once_with("This is an info message.")

    @patch('logging.Logger.warning')
    def test_logger_warning_level(self, mock_warning):
        """Test logging a message at the WARNING level."""
        logger.warning("This is a warning message.")

        # Verify `logger.warning` is called with the correct message
        mock_warning.assert_called_once_with("This is a warning message.")

    @patch('logging.Logger.error')
    def test_logger_error_level(self, mock_error):
        """Test logging a message at the ERROR level."""
        logger.error("This is an error message.")

        # Verify `logger.error` is called with the correct message
        mock_error.assert_called_once_with("This is an error message.")

    @patch('logging.Logger.debug')
    def test_logger_debug_level(self, mock_debug):
        """Test logging a message at the DEBUG level."""
        logger.debug("This is a debug message.")

        # Verify `logger.debug` is called with the correct message
        mock_debug.assert_called_once_with("This is a debug message.")

    @patch('logging.Logger.exception')
    def test_logger_exception(self, mock_exception):
        """Test logging an exception."""
        try:
            raise ValueError("A test exception occurred!")
        except ValueError:
            logger.exception("An exception was caught.")

        # Verify `logger.exception` is called with the correct message
        mock_exception.assert_called_once_with("An exception was caught.")

    def test_logger_handles_no_handlers(self):
        """Test that the logger functions even without handlers."""
        # Temporarily remove all handlers
        original_handlers = logger.handlers
        logger.handlers = []
        logger.setLevel('WARNING')
        with self.assertLogs('euler_solver', level='WARNING') as captured:
            logger.warning("This is a test warning without handlers.")
        logger.handlers = original_handlers
        logger.setLevel('ERROR')

        # Verify the logger captures the warning message
        self.assertIn("WARNING:euler_solver:This is a test warning without handlers.", captured.output)

    @patch('euler_solver.logger.logger', new_callable=MagicMock)
    def test_logger_already_initialized(self, mock_logger):
        """Test behavior when logger is already initialized."""
        # Simulate the logger already being initialized
        mock_logger_already_initialized = MagicMock(name='logger')
        # Patch the `logger` directly in `euler_solver.logger`
        with patch('euler_solver.logger.logger', mock_logger_already_initialized):
            # Re-import `logger` from the `euler_solver.logger` module
            from euler_solver.logger import logger as reimported_logger
            # Assert that the reimported logger is the patched mock
            self.assertIs(reimported_logger, mock_logger_already_initialized)


class TestJsonFormatter(unittest.TestCase):
    def test_json_formatter_format_with_exception(self):
        """Test the correct formatting of a log record with exception information."""
        # Create an instance of the JsonFormatter
        formatter = JsonFormatter()

        # Simulate an exception
        try:
            raise ValueError("This is a test exception!")
        except ValueError:
            # Capture the exception information using sys.exc_info()
            exc_info = sys.exc_info()

            # Create a log record with exception info
            log_record = logging.LogRecord(
                name="euler_solver.test",
                level=logging.ERROR,
                pathname="/path/to/test.py",
                lineno=42,
                msg="An error occurred!",
                args=None,
                exc_info=exc_info,
            )

            # Format the record
            formatted_log = formatter.format(log_record)

            # Parse the JSON result
            parsed_log = json.loads(formatted_log)

            # Verify the parsed log contents
            self.assertIn("timestamp", parsed_log)
            self.assertEqual(parsed_log["level"], "ERROR")
            self.assertEqual(parsed_log["name"], "euler_solver.test")
            self.assertEqual(parsed_log["message"], "An error occurred!")
            self.assertIn("exception", parsed_log)  # Exception info should be present
            self.assertIn("ValueError", parsed_log["exception"])  # Exception type should be present
            self.assertIn("This is a test exception!", parsed_log["exception"])  # Exception message should be present


if __name__ == "__main__":
    unittest.main()
