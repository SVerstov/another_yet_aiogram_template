from bot.setup_bot import run_bot
from config import Config, setup_logger

if __name__ == "__main__":
    setup_logger()
    config = Config()
    run_bot(config)
