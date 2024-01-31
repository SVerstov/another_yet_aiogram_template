import logging
import sys
import tomllib
from pathlib import Path

from loguru import logger


def get_module_filter(module_name):
    """
    A filter function that only returns records with a matching module name.
    """

    def filter(record):
        module = record["extra"].get("name") or record["name"].split(".")[0]
        return module == module_name

    return filter


class InterceptHandler(logging.Handler):
    """Catch standart logging records"""

    def emit(self, record):
        logger.opt(depth=6, exception=record.exc_info).log(
            record.levelname, record.getMessage()
        )


def setup_logger():
    """
    Set up logging configuration.

    """
    logger_conf_path = Path("config/logger.toml")
    logs_folder = Path("logs")

    logs_folder.mkdir(exist_ok=True)

    with logger_conf_path.open("rb") as f:
        log_conf = tomllib.load(f)

    base_config = log_conf.pop("base_config", {})
    console_config = log_conf.pop("console", {})
    with logger.catch():
        if console_config:
            logger.remove(0)
            logger.add(sys.stderr, **console_config)

        for module_name, module_conf in log_conf.items():
            module_conf = {**base_config, **module_conf}
            setup_logger_for_module(logs_folder, module_name, module_conf)

    # intercept other handlers:
    logging.basicConfig(handlers=[InterceptHandler()], level=logging.DEBUG)

    logger.info("Logging configured successfully")


def setup_logger_for_module(logs_folder: Path, module_name: str, module_conf: dict):
    """
    This method sets up a logger for a specific module, with the specified log path and configuration options.
    The logger will log to a file with the name of the module (root folder)

    If the module parameter is set to "all", the logger will not filter any log messages.
    And log all messages to the file.
    """

    file = Path(logs_folder / module_conf.pop("file", f"{module_name}.log"))

    if module_name == "all":
        module_filter = None
    else:
        module_filter = get_module_filter(module_name)
    module_conf = {"filter": module_filter, **module_conf}
    logger.add(file, **module_conf)
