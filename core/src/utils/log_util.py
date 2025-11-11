import logging
from logging.config import dictConfig
from logging.handlers import RotatingFileHandler

log_formatter = logging.Formatter("[%(levelname)s]\t%(message)s")

logger = logging.getLogger(__name__)
traceback_logger = logging.getLogger("traceback")

logger.setLevel(logging.DEBUG)
traceback_logger.setLevel(logging.ERROR)

rotating_file_handler = RotatingFileHandler(
    "./logs/log.log",
    maxBytes=1048576,
)
rotating_tb_file_handler = RotatingFileHandler(
    "./logs/tb.log",
    maxBytes=1048576,
)

rotating_file_handler.setFormatter(log_formatter)
rotating_tb_file_handler.setFormatter(log_formatter)

logger.addHandler(rotating_file_handler)
traceback_logger.addHandler(rotating_tb_file_handler)

dictConfig(
    {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "access": {
                "()": "uvicorn.logging.AccessFormatter",
                "fmt": '%(asctime)s - "%(request_line)s" %(status_code)s',
                "use_colors": True,
            },
        },
        "handlers": {
            "access": {
                "formatter": "access",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
            },
        },
        "loggers": {
            "uvicorn.access": {
                "handlers": ["access"],
                "level": "INFO",
                "propagate": False,
            },
        },
    }
)
