"""Structured logging configuration for EconoCausal.

Uses structlog for JSON (production) or console (development) logging.
Never use print() in library code — use the logger from this module.
"""

from __future__ import annotations

import logging
import sys
from typing import Any

import structlog
from structlog.types import EventDict, WrappedLogger


def _add_log_level(
    logger: WrappedLogger,
    method_name: str,
    event_dict: EventDict,
) -> EventDict:
    """Add log level to the event dict."""
    event_dict["level"] = method_name.upper()
    return event_dict


def configure_logging(log_level: str = "INFO", log_format: str = "console") -> None:
    """Configure structlog for the application.

    Args:
        log_level: One of DEBUG, INFO, WARNING, ERROR.
        log_format: 'console' for human-readable, 'json' for structured JSON.
    """
    level = getattr(logging, log_level.upper(), logging.INFO)

    shared_processors: list[Any] = [
        structlog.contextvars.merge_contextvars,
        _add_log_level,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
    ]

    if log_format == "json":
        processors: list[Any] = [
            *shared_processors,
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ]
    else:
        processors = [
            *shared_processors,
            structlog.dev.ConsoleRenderer(colors=True),
        ]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
        cache_logger_on_first_use=True,
    )

    # Also configure stdlib logging to pipe through structlog
    logging.basicConfig(
        format="%(message)s",
        level=level,
        stream=sys.stdout,
    )


def get_logger(name: str = "econocausal") -> Any:
    """Get a bound structlog logger.

    Args:
        name: Logger name, typically the module name (__name__).

    Returns:
        A bound structlog logger instance.
    """
    return structlog.get_logger(name)
