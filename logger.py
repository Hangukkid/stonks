"""Logging configuration for the stock data fetcher."""

import logging
import sys
from config import LOG_LEVEL, LOG_FORMAT


def setup_logger(name: str = __name__) -> logging.Logger:
    """Set up and configure logger."""
    logger = logging.getLogger(name)
    
    # Avoid adding multiple handlers if logger already exists
    if logger.handlers:
        return logger
    
    logger.setLevel(getattr(logging, LOG_LEVEL.upper()))
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, LOG_LEVEL.upper()))
    
    # Formatter
    formatter = logging.Formatter(LOG_FORMAT)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(console_handler)
    
    return logger


# Create a default logger instance
logger = setup_logger('stonks')
