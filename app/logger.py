"""
Centralized logging setup. Every module does:
    from app.logger import get_logger
    logger = get_logger(__name__)
"""

import logging
import sys

from app.config import settings


def _configure_root_logger() -> None:
    root = logging.getLogger()
    root.setLevel(settings.LOG_LEVEL.upper())

    if root.handlers:
        return

    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    root.addHandler(handler)

    logging.getLogger("httpx").setLevel(logging.WARNING)


_configure_root_logger()


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
