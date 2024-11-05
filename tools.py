import logging
import sys


def set_up_logger(logger_name="ks-xml-logger") -> logging.Logger:
    logger = logging.getLogger(logger_name)
    logging.basicConfig(
        level=logging.INFO,  # Set the minimum logging level
        format="%(asctime)s [%(levelname)s] %(message)s",  # Format the log messages
        stream=sys.stdout,  # Output the logs to standard output
    )
    return logger


def get_error_details(e):
    return f"{type(e)}: {e}"
