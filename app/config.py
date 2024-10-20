import os
from typing import Literal

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
    

config = Config()
