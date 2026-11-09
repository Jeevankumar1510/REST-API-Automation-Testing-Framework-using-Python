"""
Centralized Logging Utility for API Automation Testing.
Configures formatted console and file logging.
"""

import logging
import sys
from pathlib import Path
from typing import Optional

from config.config import LOG_FILE_PATH, REPORTS_DIR


def setup_logger(
    name: str = "API_Automation",
    log_file: Optional[Path] = LOG_FILE_PATH,
    level: int = logging.INFO
) -> logging.Logger:
    """
    Configure and return a standardized logger instance.
    Logs to both console (stdout) and file.
    """
    logger = logging.getLogger(name)

    # Avoid adding duplicate handlers if logger was already created
    if logger.hasHandlers():
        return logger

    logger.setLevel(level)
    logger.propagate = False

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File Handler
    if log_file:
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, mode="a", encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str = "API_Automation") -> logging.Logger:
    """Convenience getter for loggers with hierarchical names."""
    return setup_logger(name)

