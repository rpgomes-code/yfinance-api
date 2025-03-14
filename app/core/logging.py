"""Logging configuration for the YFinance API.

This module sets up logging for the application using Python's logging module.
"""
import logging
import logging.config
import json
import sys
import os
from datetime import datetime, timezone
from logging import Logger, LoggerAdapter
from typing import Any, Dict, Union

from app.core.config import settings

# Define custom log levels
TRACE_LEVEL = 5  # More detailed than DEBUG


class JsonFormatter(logging.Formatter):
    """
    Formatter for JSON-structured logs.

    This formatter outputs logs in JSON format, which is useful for log
    aggregation services like ELK stack, Datadog, etc.
    """

    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as JSON.

        Args:
            record: Log record to format

        Returns:
            str: JSON formatted log
        """
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "process": record.process,
            "thread": record.thread,
        }

        # Add exception info if available
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": self.formatException(record.exc_info),
            }

        # Add extra fields if available
        if hasattr(record, "data") and isinstance(record.data, dict):
            log_data.update(record.data)

        return json.dumps(log_data)


def setup_logging() -> None:
    """
    Configure application logging.

    This function sets up logging based on application settings.
    """
    # Add custom trace level
    logging.addLevelName(TRACE_LEVEL, "TRACE")

    # Define logger for trace level
    def trace(self, message, *args, **kwargs):
        if self.isEnabledFor(TRACE_LEVEL):
            self._log(TRACE_LEVEL, message, args, **kwargs)

    logging.Logger.trace = trace

    # Configure basic logging
    log_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": settings.LOG_FORMAT,
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "json": {
                "()": JsonFormatter,
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": settings.LOG_LEVEL,
                "formatter": "standard" if settings.ENVIRONMENT in ["development", "testing"] else "json",
                "stream": sys.stdout,
            },
        },
        "loggers": {
            "": {  # root logger
                "handlers": ["console"],
                "level": settings.LOG_LEVEL,
                "propagate": True,
            },
            "uvicorn": {
                "handlers": ["console"],
                "level": settings.LOG_LEVEL,
                "propagate": False,
            },
            "uvicorn.access": {
                "handlers": ["console"],
                "level": "INFO",
                "propagate": False,
            },
            "app": {
                "handlers": ["console"],
                "level": settings.LOG_LEVEL,
                "propagate": False,
            },
        },
    }

    # Add file handler in production
    if settings.ENVIRONMENT == "production":
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)

        log_config["handlers"]["file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "level": settings.LOG_LEVEL,
            "formatter": "json",
            "filename": os.path.join(log_dir, "app.log"),
            "maxBytes": 10485760,  # 10 MB
            "backupCount": 5,
        }

        for logger_name in log_config["loggers"]:
            log_config["loggers"][logger_name]["handlers"].append("file")

    # Apply configuration
    logging.config.dictConfig(log_config)

    # Log startup message
    logger = logging.getLogger("app")
    logger.info(
        f"Logging initialized with level {settings.LOG_LEVEL} in {settings.ENVIRONMENT} environment"
    )


class LoggerAdapter(logging.LoggerAdapter):
    """
    Logger adapter for adding contextual information to logs.

    This adapter allows attaching extra information to all log messages
    from a specific logger.
    """

    def process(self, msg: str, kwargs: Dict[str, Any]) -> tuple:
        """
        Process log message to add context information.

        Args:
            msg: Log message
            kwargs: Keyword arguments

        Returns:
            tuple: Processed message and kwargs
        """
        if "extra" not in kwargs:
            kwargs["extra"] = {}

        if hasattr(self, "data") and isinstance(self.data, dict):
            if "data" not in kwargs["extra"]:
                kwargs["extra"]["data"] = {}

            kwargs["extra"]["data"].update(self.data)

        return msg, kwargs


def get_logger(name: str, **context) -> Union[Logger, LoggerAdapter]:
    """
    Get a logger with context information.

    Args:
        name: Logger name
        **context: Context information to include in all logs

    Returns:
        logging.Logger: Logger with context information
    """
    logger = logging.getLogger(name)

    if not context:
        return logger

    adapter = LoggerAdapter(logger, {})
    adapter.data = context

    return adapter