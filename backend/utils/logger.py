"""
Shared Rich-based logger for every agent.
Usage:
    from utils.logger import get_logger
    log = get_logger("news_agent")
    log.info("Fetched 12 articles")
    log.debug("[RAW MATCH] row_label='Crude Throughput' value='24.6 MMT'")
"""
import logging
import os
from rich.logging import RichHandler

def get_logger(name: str) -> logging.Logger:
    level = os.getenv("LOG_LEVEL", "INFO").upper()
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger  # avoid duplicate handlers on reimport
    logger.setLevel(level)
    handler = RichHandler(rich_tracebacks=True, show_path=False)
    handler.setFormatter(logging.Formatter("%(message)s", datefmt="[%X]"))
    logger.addHandler(handler)
    return logger
