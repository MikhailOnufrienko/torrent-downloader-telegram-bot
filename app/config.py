import os
import sys
from typing import Literal

from loguru import logger
from pydantic import PostgresDsn, SecretStr
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
    POSTGRES_DSN: PostgresDsn = 'postgresql+asyncpg://postgres:postgres@localhost:5432/torrent_dl'
    MAXIMUM_TORRENTS_TO_SEND: int = 16
    TELEGRAM_BOT_TOKEN: str
    QBITTORRENT_CLIENT_DSN: str = "http://localhost:8080"
    QBITTORRENT_AUTH_USER: str = "admin"
    QBITTORRENT_AUTH_PASS: SecretStr

    @property
    def postgres_dsn(self) -> str:
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
    def qbittorrent_auth_pass(self):
        return self.QBITTORRENT_AUTH_PASS.get_secret_value()
    
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
