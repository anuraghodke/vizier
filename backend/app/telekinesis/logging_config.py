"""
Logging configuration for Telekinesis system.

Provides structured logging for agent execution, state transitions,
and performance monitoring with Rich formatting.
"""

import logging
import sys
from typing import Optional
from rich.logging import RichHandler
from rich.console import Console


def setup_telekinesis_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    use_rich: bool = True,
) -> logging.Logger:
    """
    Configure logging for Telekinesis system with Rich formatting.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional file path for log output
        use_rich: Whether to use Rich handler for console output (default: True)

    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger("telekinesis")
    logger.setLevel(getattr(logging, level.upper()))

    # Prevent duplicate handlers
    if logger.handlers:
        return logger

    # Console handler with Rich formatting
    if use_rich:
        console = Console(stderr=False)
        console_handler = RichHandler(
            console=console,
            show_time=True,
            show_path=False,
            markup=True,
            rich_tracebacks=True,
            tracebacks_show_locals=False,
        )
        # Rich handles its own formatting
        console_handler.setFormatter(logging.Formatter("%(message)s"))
    else:
        # Fallback to standard logging
        console_handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(name)s.%(funcName)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)

    # File handler (if specified) - always use standard formatting for files
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(name)s.%(funcName)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(file_formatter)
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
