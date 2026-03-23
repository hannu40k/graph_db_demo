"""Structured logging setup using structlog with stdlib integration."""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Any

import structlog

from app.config import AppConfig


def configure_logging(config: AppConfig, *, cli_mode: bool = False) -> None:
    """Configure structlog and stdlib logging.

    Args:
        config: Application config (uses config.logging for level/file/output).
        cli_mode: When True, logs to stdout only regardless of config.output.
    """
    log_cfg = config.logging
    level = getattr(logging, log_cfg.level.upper(), logging.INFO)

    shared_processors: list[Any] = [
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.CallsiteParameterAdder(
            [structlog.processors.CallsiteParameter.PATHNAME],
            additional_ignores=["logging"],
        ),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.ExceptionRenderer(),
    ]

    structlog.configure(
        processors=shared_processors
        + [
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=shared_processors,
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            structlog.processors.JSONRenderer(),
        ],
    )

    handlers: list[logging.Handler] = []

    use_stdout = cli_mode or log_cfg.output in ("stdout", "both")
    use_file = not cli_mode and log_cfg.output in ("file", "both")

    if use_stdout:
        stream = sys.stderr if cli_mode else sys.stdout
        stdout_handler = logging.StreamHandler(stream)
        stdout_handler.setFormatter(formatter)
        handlers.append(stdout_handler)

    if use_file:
        log_path = Path(log_cfg.file_path)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_path)
        file_handler.setFormatter(formatter)
        handlers.append(file_handler)

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    for handler in handlers:
        root_logger.addHandler(handler)
    root_logger.setLevel(level)

def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """Return a bound structlog logger.

    Args:
        name: Optional logger name (e.g. ``"app.services.graph"``).

    Returns:
        A structlog BoundLogger bound to the given name.
    """
    return structlog.get_logger(name)
