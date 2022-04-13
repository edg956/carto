from typing import Optional

from pydantic import BaseModel
import yaml


class DatabaseConfig(BaseModel):
    host: str
    port: Optional[str]
    database: Optional[str]
    user: str
    password: str
    database_class: str


class Config(BaseModel):
    db_config: DatabaseConfig


def init_config(config_path: str = 'config/config.yml'):
    with open(config_path) as f:
        data = yaml.load(f, Loader=yaml.Loader)

    return Config(**data)


settings = init_config()
