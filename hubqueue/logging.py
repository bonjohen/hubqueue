"""
Logging module for HubQueue.
"""
import os
import logging
import sys
from pathlib import Path

# Define log levels
LOG_LEVELS = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL
}

# Default log format
DEFAULT_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Create logger
logger = logging.getLogger("hubqueue")


def setup_logging(level="info", log_file=None, log_format=None):
    """
    Set up logging configuration.
    
    Args:
        level (str): Log level (debug, info, warning, error, critical)
        log_file (str, optional): Path to log file. If None, logs to console only.
        log_format (str, optional): Log format string. If None, uses default format.
    """
    # Get log level
    log_level = LOG_LEVELS.get(level.lower(), logging.INFO)
    
    # Set logger level
    logger.setLevel(log_level)
    
    # Clear existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create formatter
    formatter = logging.Formatter(log_format or DEFAULT_LOG_FORMAT)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Create file handler if log_file is specified
    if log_file:
        # Create directory if it doesn't exist
        log_dir = os.path.dirname(log_file)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)


def get_logger():
    """
    Get the HubQueue logger.
    
    Returns:
        logging.Logger: HubQueue logger
    """
    return logger


# Initialize logging with default settings
setup_logging(
    level=os.environ.get("HUBQUEUE_LOG_LEVEL", "info"),
    log_file=os.environ.get("HUBQUEUE_LOG_FILE")
)
