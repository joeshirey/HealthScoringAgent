"""
This module provides a centralized logging configuration for the application.
"""
import logging
import sys


def setup_logging() -> None:
    """
    Configures a standardized logger for the entire application.

    This function sets up a basic logger that writes to standard output
    with a consistent format, including a timestamp, logger name, log level,
    and message. It should be called once when the application starts.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stdout,  # Direct logs to standard output.
    )
