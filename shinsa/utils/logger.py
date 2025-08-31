import os
import sys
import logging
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler

# PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
# PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
print(f"Project Root: {PROJECT_ROOT}")
LOG_DIR = os.path.join(PROJECT_ROOT, "logs")
print(f"Log Directory: {LOG_DIR}")
os.makedirs(LOG_DIR, exist_ok=True)


def get_logger(name: str = "app_logger", console: bool = True) -> logging.Logger:
    logger = logging.getLogger(name)

    if not logger.handlers:
        logger.setLevel(logging.DEBUG)  # Capture all logs

        date_str = datetime.now().strftime("%Y-%m-%d")
        log_name = name + "_" + date_str
        # 1️⃣ File handler for all logs
        all_log_file = os.path.join(LOG_DIR, f"{log_name}.log")
        all_handler = TimedRotatingFileHandler(all_log_file, when="midnight", interval=1, backupCount=7, encoding="utf-8")
        all_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter(fmt="[{asctime}] | {levelname:^8} | {name}:{funcName} | {message}", datefmt="%Y-%m-%d %H:%M:%S", style="{")
        all_handler.setFormatter(formatter)
        logger.addHandler(all_handler)

        # 2️⃣ File handler for error/critical logs only
        error_log_file = os.path.join(LOG_DIR, f"{log_name}_error.log")
        error_handler = TimedRotatingFileHandler(error_log_file, when="midnight", interval=1, backupCount=7, encoding="utf-8")
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        logger.addHandler(error_handler)

        # 3️⃣ Optional console output
        if console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.INFO)
            console_formatter = logging.Formatter(fmt="[{asctime}] | {levelname:^8} | {name}:{funcName} | {message}", datefmt="%H:%M:%S", style="{")
            console_handler.setFormatter(console_formatter)
            logger.addHandler(console_handler)

    return logger
