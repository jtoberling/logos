"""
Logging configuration for Logos.

Provides structured logging with timestamped format and configurable log levels.
Supports both development and production environments.
"""

import logging
import sys
from typing import Optional, Dict, Any
from pathlib import Path

try:
    import structlog
    STRUCTLOG_AVAILABLE = True
except ImportError:
    STRUCTLOG_AVAILABLE = False


class LogosLogger:
    """
    Centralized logging configuration for Logos.

    Features:
    - Timestamped log format
    - Configurable log levels
    - Structured logging support (if structlog available)
    - File and console output
    - Environment-based configuration
    """

    def __init__(self, config=None):
        """
        Initialize logging configuration.

        Args:
            config: Configuration object with log_level and logs_dir attributes
        """
        self.config = config
        self._configured = False

    def configure_logging(
        self,
        log_level: str = "INFO",
        log_file: Optional[str] = None,
        enable_structlog: bool = True
    ) -> None:
        """
        Configure logging with timestamped format and appropriate handlers.

        Args:
            log_level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_file: Optional log file path
            enable_structlog: Whether to use structured logging if available
        """
        if self._configured:
            return

        # Convert string log level to logging level
        numeric_level = getattr(logging, log_level.upper(), logging.INFO)

        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(numeric_level)

        # Clear existing handlers
        root_logger.handlers.clear()

        # Create formatter with timestamp
        formatter = logging.Formatter(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(numeric_level)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

        # File handler (if log file specified)
        if log_file:
            try:
                log_path = Path(log_file)
                log_path.parent.mkdir(parents=True, exist_ok=True)

                file_handler = logging.FileHandler(log_path)
                file_handler.setLevel(numeric_level)
                file_handler.setFormatter(formatter)
                root_logger.addHandler(file_handler)
            except Exception as e:
                # Log to console if file logging fails
                console_handler.emit(
                    logging.LogRecord(
                        name="logos.logging",
                        level=logging.WARNING,
                        pathname="",
                        lineno=0,
                        msg=f"Failed to configure file logging: {e}",
                        args=(),
                        exc_info=None
                    )
                )

        # Configure structlog if available and enabled
        if STRUCTLOG_AVAILABLE and enable_structlog:
            self._configure_structlog()
        elif STRUCTLOG_AVAILABLE and not enable_structlog:
            # Disable structlog if explicitly disabled
            import structlog
            structlog.configure(
                processors=[structlog.stdlib.filter_by_level],
                logger_factory=structlog.stdlib.LoggerFactory(),
                wrapper_class=structlog.stdlib.BoundLogger,
                cache_logger_on_first_use=True,
            )

        self._configured = True

        # Log successful configuration
        logger = logging.getLogger(__name__)
        logger.info(f"Logging configured with level {log_level}")
        if log_file:
            logger.info(f"Log file: {log_file}")

    def _configure_structlog(self) -> None:
        """Configure structured logging with structlog."""
        import structlog

        # Configure structlog with timestamped JSON format
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                # Output to standard logging
                structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )

    def get_logger(self, name: str) -> logging.Logger:
        """
        Get a configured logger instance.

        Args:
            name: Logger name (usually __name__)

        Returns:
            Configured logger instance
        """
        return logging.getLogger(name)


# Global logger instance
_logger_instance: Optional[LogosLogger] = None


def get_logger(name: str) -> logging.Logger:
    """
    Get a configured logger instance.

    Args:
        name: Logger name (usually __name__)

    Returns:
        Configured logger instance
    """
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = LogosLogger()
    return _logger_instance.get_logger(name)


def configure_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    config=None
) -> None:
    """
    Configure logging for the entire application.

    Args:
        log_level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path
        config: Configuration object with log_level and logs_dir attributes
    """
    global _logger_instance

    if _logger_instance is None:
        _logger_instance = LogosLogger(config)

    # Get log level from config if available
    if config and hasattr(config, 'log_level'):
        config_log_level = getattr(config, 'log_level', None)
        if isinstance(config_log_level, str):
            log_level = config_log_level

    # Get log file from config if available
    if config and hasattr(config, 'logs_dir') and log_file is None:
        config_logs_dir = getattr(config, 'logs_dir', None)
        if isinstance(config_logs_dir, str):
            log_file_path = Path(config_logs_dir) / "logos.log"
            log_file = str(log_file_path)

    _logger_instance.configure_logging(
        log_level=log_level,
        log_file=log_file,
        enable_structlog=True
    )


def get_log_level_from_env(default: str = "INFO") -> str:
    """
    Get log level from environment variable.

    Args:
        default: Default log level if not set

    Returns:
        Log level string
    """
    import os
    return os.getenv("LOG_LEVEL", default).upper()


# Convenience functions for different log levels
def debug(message: str, *args, **kwargs) -> None:
    """Log debug message."""
    get_logger(__name__).debug(message, *args, **kwargs)


def info(message: str, *args, **kwargs) -> None:
    """Log info message."""
    get_logger(__name__).info(message, *args, **kwargs)


def warning(message: str, *args, **kwargs) -> None:
    """Log warning message."""
    get_logger(__name__).warning(message, *args, **kwargs)


def error(message: str, *args, **kwargs) -> None:
    """Log error message."""
    get_logger(__name__).error(message, *args, **kwargs)


def critical(message: str, *args, **kwargs) -> None:
    """Log critical message."""
    get_logger(__name__).critical(message, *args, **kwargs)