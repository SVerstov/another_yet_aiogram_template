from config import Config, setup_loguru
from loguru import logger

if __name__ == "__main__":
    setup_loguru()
    config = Config()
    bot_logger = logger.bind(module="bot")
    bot_logger.info("kcjfl=>ksdjkfl=>")
    pass
