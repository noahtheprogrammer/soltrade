import logging
from logging.handlers import RotatingFileHandler
from logging import StreamHandler
import sys


# Custom formatter to support colors in console
class CustomFormatter(logging.Formatter):
    grey = "\x1b[38;21m"
    green = "\x1b[32;21m"
    yellow = "\x1b[33;21m"
    red = "\x1b[31;21m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = "%(asctime)s       %(message)s"

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: green + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record) -> str:
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt="%Y-%m-%d %H:%M:%S")
        return formatter.format(record)


class AutoFlushStreamHandler(StreamHandler):
    def emit(self, record):
        super().emit(record)
        self.flush()


def setup_logger(name, log_file, level=logging.INFO, add_to_general=False) -> logging.Logger:
    """Function to set up a logger with rotating file handler and console output."""
    # Formatter without color codes for file output
    file_formatter = logging.Formatter("%(asctime)s     %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

    # File handler setup
    file_handler = RotatingFileHandler(log_file, maxBytes=1000000, backupCount=5)
    file_handler.setFormatter(file_formatter)

    # Logger setup
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(file_handler)

    # Console handler with color codes
    console_handler = AutoFlushStreamHandler(sys.stdout)
    console_handler.setFormatter(CustomFormatter())
    logger.addHandler(console_handler)

    if add_to_general:
        general_handler = RotatingFileHandler('general_log.log', maxBytes=1000000, backupCount=5)
        general_handler.setFormatter(file_formatter)
        logger.addHandler(general_handler)

    return logger


# Creating two loggers, with transaction logger also writing to general log
log_general = setup_logger('general_logger', 'general_log.log', level=logging.DEBUG)
log_transaction = setup_logger('transaction_logger', 'transaction_log.log', add_to_general=True, level=logging.DEBUG)
