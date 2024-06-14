import os
from datetime import datetime
from logging import (CRITICAL, INFO, FileHandler, Formatter, Logger,
                     StreamHandler, getLogger)

from colorama import Fore, Style

LOGS_DIR = 'logs'

def get_logger(path: str | None = None, level: int = INFO) -> Logger:
    logger = getLogger(path)
    logger.setLevel(level)
    return logger


def setup_logger(root_logger: Logger, level: int = INFO) -> None:
    """
    Setup formatter with colors for terminal, without colors for log file.
    Skips library loggers
    """
    if not os.path.exists(LOGS_DIR):
        # Crear la carpeta si no existe
        os.makedirs(LOGS_DIR)
    log_handler = StreamHandler()
    formatter = Formatter(
        f"[{Fore.LIGHTCYAN_EX}%(asctime)s{Style.RESET_ALL}][%(name)s][%(levelname)s] -> %(message)s"
    )
    log_handler.setFormatter(formatter)
    fileHandler = FileHandler(f"{LOGS_DIR}/{datetime.today().date()}.log")
    file_formatter = Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    fileHandler.setFormatter(file_formatter)
    for handler in (log_handler, fileHandler):
        handler.setLevel(level)
        root_logger.addHandler(handler)
    for module in ("httpx", "httpcore"):
        # ignored loggers
        logger = getLogger(module)
        logger.setLevel(CRITICAL)
        logger.propagate = False
