import logging
import sys
import json
import datetime
import os
from typing import Dict, Any, Optional
import colorlog


class CustomJSONFormatter(logging.Formatter):
    """
    Formatter that outputs JSON strings after parsing the log record.
    """

    def __init__(self, **kwargs):
        self.json_fields = kwargs.pop("json_fields", [])
        self.format_string = "{message}"
        self.default_fields = {"level", "message", "timestamp", "logger_name"}
        super().__init__(self.format_string, style="{")

    def format(self, record: logging.LogRecord) -> str:
        """Format the log record as JSON."""
        record_dict = {
            "level": record.levelname,
            "message": record.getMessage(),
            "timestamp": datetime.datetime.fromtimestamp(record.created).isoformat(),
            "logger_name": record.name
        }

        # Add exception info if available
        if record.exc_info:
            record_dict["exception"] = self.formatException(record.exc_info)

        # Add file, line number and function
        record_dict["file"] = record.pathname
        record_dict["line"] = record.lineno
        record_dict["function"] = record.funcName

        # Add any custom fields
        for field in self.json_fields:
            if hasattr(record, field):
                record_dict[field] = getattr(record, field)

        return json.dumps(record_dict)


def setup_logging(
        log_level: str = "INFO",
        log_format: str = "json",
        log_file: Optional[str] = None
) -> None:
    """
    Set up logging configuration.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Log format (json or pretty)
        log_file: Optional log file path
    """
    # Set up root logger
    root_logger = logging.getLogger()

    # Clear existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Set log level
    level = getattr(logging, log_level.upper())
    root_logger.setLevel(level)

    handlers = []

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)

    # Set formatter based on format
    if log_format.lower() == "json":
        formatter = CustomJSONFormatter()
    else:
        # Pretty colored logs for console
        formatter = colorlog.ColoredFormatter(
            "%(log_color)s%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            }
        )

    console_handler.setFormatter(formatter)
    handlers.append(console_handler)

    # Create file handler if log_file is specified
    if log_file:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(log_file), exist_ok=True)

        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        handlers.append(file_handler)

    # Add handlers to root logger
    for handler in handlers:
        root_logger.addHandler(handler)

    # Create a separate logger for third-party libraries
    for logger_name in ["uvicorn", "sqlalchemy.engine"]:
        logging.getLogger(logger_name).setLevel(logging.WARNING)