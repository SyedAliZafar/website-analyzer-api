"""
Centralized logging configuration.
Keeps logging consistent across services and modules.
"""

import logging


def setup_logging(level: int = logging.INFO) -> None:
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


# Convenience logger factory
def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
