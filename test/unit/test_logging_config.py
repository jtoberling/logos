"""
Unit tests for logging configuration.

Tests the LogosLogger class and logging utilities.
"""

import logging
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

from src.logging_config import (
    LogosLogger,
    get_logger,
    configure_logging,
    get_log_level_from_env,
    debug, info, warning, error, critical
)


class TestLogosLogger:
    """Test LogosLogger class functionality."""

    def setup_method(self):
        """Reset logging configuration before each test."""
        # Clear existing handlers
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        # Reset logger instances
        import src.logging_config
        if hasattr(src.logging_config, '_logger_instance'):
            delattr(src.logging_config, '_logger_instance')

    def test_init(self):
        """Test LogosLogger initialization."""
        config = MagicMock()
        logger = LogosLogger(config)
        assert logger.config == config
        assert not logger._configured

    def test_configure_logging_basic(self):
        """Test basic logging configuration."""
        logger = LogosLogger()

        with patch('src.logging_config.STRUCTLOG_AVAILABLE', False):
            logger.configure_logging(log_level="DEBUG")

        assert logger._configured
        root_logger = logging.getLogger()
        assert len(root_logger.handlers) > 0

    def test_configure_logging_with_structlog(self):
        """Test logging configuration with structlog available."""
        logger = LogosLogger()

        with patch('src.logging_config.STRUCTLOG_AVAILABLE', True):
            # Mock the import since structlog is not installed
            mock_structlog = MagicMock()
            with patch.dict('sys.modules', {'structlog': mock_structlog}):
                logger.configure_logging(log_level="INFO", enable_structlog=True)

                mock_structlog.configure.assert_called_once()

    def test_configure_logging_with_file(self):
        """Test logging configuration with file output."""
        logger = LogosLogger()

        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = os.path.join(temp_dir, "test.log")

            with patch('src.logging_config.STRUCTLOG_AVAILABLE', False):
                logger.configure_logging(log_level="INFO", log_file=log_file)

            # Check that file handler was added
            root_logger = logging.getLogger()
            file_handlers = [h for h in root_logger.handlers if isinstance(h, logging.FileHandler)]
            assert len(file_handlers) > 0
            assert file_handlers[0].baseFilename == log_file

    def test_configure_logging_directory_creation(self):
        """Test that log directory is created if it doesn't exist."""
        logger = LogosLogger()

        with tempfile.TemporaryDirectory() as temp_dir:
            log_dir = os.path.join(temp_dir, "logs")
            log_file = os.path.join(log_dir, "test.log")

            with patch('src.logging_config.STRUCTLOG_AVAILABLE', False):
                logger.configure_logging(log_level="INFO", log_file=log_file)

            assert os.path.exists(log_dir)

    def test_configure_logging_idempotent(self):
        """Test that configure_logging is idempotent."""
        logger = LogosLogger()

        with patch('src.logging_config.STRUCTLOG_AVAILABLE', False):
            logger.configure_logging(log_level="INFO")
            initial_handlers = len(logging.getLogger().handlers)

            logger.configure_logging(log_level="DEBUG")
            # Should not add duplicate handlers
            assert len(logging.getLogger().handlers) == initial_handlers

    def test_get_logger_via_class(self):
        """Test get_logger via LogosLogger class method."""
        logos_logger = LogosLogger()
        logger = logos_logger.get_logger("test_module")
        assert isinstance(logger, logging.Logger)
        assert logger.name == "test_module"

    def test_configure_logging_via_class(self):
        """Test configure_logging via LogosLogger class method."""
        logos_logger = LogosLogger()
        with patch('src.logging_config.STRUCTLOG_AVAILABLE', False):
            logos_logger.configure_logging(log_level="WARNING")

        assert logos_logger._configured

    def test_get_log_level_from_env(self):
        """Test getting log level from environment."""
        # Test default
        level = get_log_level_from_env()
        assert level == "INFO"

        # Test with env var
        with patch.dict(os.environ, {'LOG_LEVEL': 'DEBUG'}):
            level = get_log_level_from_env()
            assert level == "DEBUG"

    def test_get_log_level_from_env_invalid(self):
        """Test invalid log level from environment."""
        with patch.dict(os.environ, {'LOG_LEVEL': 'INVALID'}):
            level = get_log_level_from_env()
            assert level == "INVALID"  # Returns as-is, validation happens elsewhere

    def test_convenience_functions_exist(self):
        """Test that convenience functions are defined and callable."""
        # Just test that the functions exist and are callable
        assert callable(debug)
        assert callable(info)
        assert callable(warning)
        assert callable(error)
        assert callable(critical)

    def test_structlog_processor(self):
        """Test structlog processor configuration."""
        with patch('src.logging_config.STRUCTLOG_AVAILABLE', True):
            # Mock the import since structlog is not installed
            mock_structlog = MagicMock()
            with patch.dict('sys.modules', {'structlog': mock_structlog}):
                logger = LogosLogger()
                logger.configure_logging(enable_structlog=True)

                # Verify structlog was configured
                mock_structlog.configure.assert_called_once()

    def test_log_level_mapping(self):
        """Test log level string to constant mapping."""
        logger = LogosLogger()

        # Test that different log levels can be set without error
        test_cases = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

        for level_str in test_cases:
            # Reset logger configuration
            logger._configured = False
            with patch('src.logging_config.STRUCTLOG_AVAILABLE', False):
                logger.configure_logging(log_level=level_str)
                # Just verify it doesn't raise an error
                assert logger._configured

    def test_invalid_log_level(self):
        """Test handling of invalid log level."""
        logger = LogosLogger()

        with patch('src.logging_config.STRUCTLOG_AVAILABLE', False):
            logger.configure_logging(log_level="INVALID")

        # Should default to INFO
        root_logger = logging.getLogger()
        assert root_logger.level == logging.INFO

    def test_formatter_configuration(self):
        """Test that custom formatter is applied."""
        logger = LogosLogger()

        with patch('src.logging_config.STRUCTLOG_AVAILABLE', False):
            logger.configure_logging()

        root_logger = logging.getLogger()
        console_handler = next((h for h in root_logger.handlers if isinstance(h, logging.StreamHandler)), None)
        assert console_handler is not None

        # Check that formatter contains expected elements
        formatter = console_handler.formatter
        assert formatter is not None
        # The formatter should include timestamp, level, etc.
        assert "%(asctime)s" in formatter._fmt or "asctime" in str(formatter._fmt)

    def test_file_handler_with_existing_directory(self):
        """Test file logging when directory already exists."""
        logger = LogosLogger()

        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = os.path.join(temp_dir, "existing.log")

            with patch('src.logging_config.STRUCTLOG_AVAILABLE', False):
                logger.configure_logging(log_file=log_file)

            # File should be created
            assert os.path.exists(log_file)