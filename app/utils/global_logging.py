import logging

import colorlog

from app.config import get_settings

settings = get_settings()

# Create a colored formatter
formatter = colorlog.ColoredFormatter(
    "%(log_color)s%(levelname)s%(reset)s - %(name)s - %(message)s",
    datefmt=None,
    reset=True,
    log_colors={
        "DEBUG": "cyan",
        "INFO": "green",
        "WARNING": "yellow",
        "ERROR": "red",
        "CRITICAL": "red,bg_white",
    },
    secondary_log_colors={},
    style="%",
)
# Configure logging with colored formatter
handler = colorlog.StreamHandler()
handler.setFormatter(formatter)

logging.basicConfig(
    level=getattr(logging, settings.log_level),
    handlers=[handler],
)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the specified name.

    Args:
        name (str): The name of the logger.

    Returns:
        logging.Logger: Configured logger instance.
    """
    return logging.getLogger(name)
