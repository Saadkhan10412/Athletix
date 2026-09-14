"""
ATHLETIX — Centralized Logging Setup
backend/app/utils/logger.py

Provides structured standard-library logging across all backend modules and services.

Working & Usage:
- Standardizes log formatting: timestamps, log severity levels, module namespace, and message content.
- Dynamically configures log thresholds based on runtime environment (INFO in dev, WARNING in prod).
- Usage:
    from app.utils.logger import get_logger
    logger = get_logger(__name__)
    logger.info("Video %s processed successfully", video_id)
"""

import logging
import sys

from app.core.config import settings

_configured = False


def configure_logging() -> None:
    """
    Configures root logger handlers and timestamp format once per process lifecycle.
    """
    global _configured
    if _configured:
        return

    level = logging.INFO if settings.APP_ENV == "development" else logging.WARNING

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )

    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(handler)
    _configured = True


def get_logger(name: str) -> logging.Logger:
    """
    Returns a configured Logger instance for the specified module namespace.
    """
    configure_logging()
    return logging.getLogger(name)
