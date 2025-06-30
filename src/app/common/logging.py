import logging
import logging.config
from pathlib import Path

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "()": "colorlog.ColoredFormatter",
            "format": "%(asctime)s - %(log_color)s%(name)s - %(levelname)s - %(reset)s%(message)s",
            "log_colors": {
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "bold_red",
            },
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "level": "INFO",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "logs/app.log",
            "maxBytes": 1024 * 1024 * 5,
            "backupCount": 5,
            "formatter": "standard",
            "level": "DEBUG",
        },
    },
    "loggers": {
        "httpcore": {"level": "WARNING"},
        "watchfiles": {"level": "WARNING"},
        "aiormq": {"level": "WARNING"},
        "apscheduler": {"level": "WARNING"},
        "faststream": {"level": "INFO"},
        "src.app.services": {"level": "INFO"},
    },
    "root": {
        "handlers": ["console", "file"],
        "level": "DEBUG",
    },
}

Path("logs").mkdir(exist_ok=True)
logging.config.dictConfig(LOGGING_CONFIG)
