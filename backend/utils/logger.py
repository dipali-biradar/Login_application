import logging
from logging.handlers import RotatingFileHandler
import os
import sys

# Define base directory and logs directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGS_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOGS_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOGS_DIR, "app.log")

def setup_logger(name: str = "auth_app") -> logging.Logger:
    """
    Sets up a centralized logger with standard console output and
    production-grade rotating file logging.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)  # Capture all levels; handlers will filter

    # Prevent duplicate handlers if logger is already configured
    if logger.hasHandlers():
        return logger

    # Formatter for logs
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Console Handler (Stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File Handler (Rotating)
    file_handler = RotatingFileHandler(
        filename=LOG_FILE,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger

# Expose a default logger instance
logger = setup_logger()
