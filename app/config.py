import os
import sys
from typing import Literal

from loguru import logger
from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

load_dotenv(override=True)

dir_path = os.path.dirname(os.path.realpath(__file__))
model_config = SettingsConfigDict(
    env_file=os.path.join(dir_path, '../.env'),
    env_file_encoding='utf-8',
)


class Config(BaseSettings):
    model_config = model_config

    MODE: Literal['DEV', 'PROD', 'TEST'] = 'DEV'
    POSTGRES_DSN: PostgresDsn = 'postgresql+asyncpg://postgres:postgres@localhost:5432/torrent_downloader'
    MAXIMUM_TORRENTS_TO_SEND: int = 16
    TELEGRAM_BOT_TOKEN: str

    @property
    def postgres_dsn(self) -> str:
        if self.is_dev_mode:
            return self.POSTGRES_DSN.unicode_string() + "_dev"
        if self.is_test_mode:
            return self.POSTGRES_DSN.unicode_string() + "_test"
        return self.POSTGRES_DSN.unicode_string()
    
    @property
    def is_test_mode(self) -> bool:
        return self.MODE == "TEST"
    
    @property
    def is_dev_mode(self) -> bool:
        return self.MODE == "DEV"
    
    @property
    def logger(self):
        logger.remove()
        logger.add(
            sys.stdout,
            format="<green>{time}</green> | <level>{level}</level> | <cyan>{name}</cyan> | {message}",
            level="DEBUG", enqueue=True, backtrace=True, diagnose=True
        )
        logger.add("downloader.log", rotation="50 MB", retention="10 days", compression="zip")
        return logger
    

config = Config()
