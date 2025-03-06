import logging.config
import logging.handlers
from pathlib import Path


def setup_logging():
    config_path = Path(__file__).parent / "logger_config.ini"
    logging.config.fileConfig(config_path, disable_existing_loggers=False)
