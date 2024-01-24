from bot import run_bot
from config import Config, setup_loguru

if __name__ == "__main__":
    setup_loguru()
    config = Config()
    run_bot(config)
