"""
Logging configuration for Telekinesis system.

Provides structured logging for agent execution, state transitions,
and performance monitoring.
"""

import logging
import sys
from typing import Optional


def setup_telekinesis_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
) -> logging.Logger:
    """
    Configure logging for Telekinesis system.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional file path for log output

    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger("telekinesis")
    logger.setLevel(getattr(logging, level.upper()))

    # Prevent duplicate handlers
    if logger.handlers:
        return logger

    # Create formatter
    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s.%(funcName)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (if specified)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str = "telekinesis") -> logging.Logger:
    """
    Get a logger instance.

    Args:
        name: Logger name (default: "telekinesis")

    Returns:
        Logger instance
    """
    return logging.getLogger(name)
