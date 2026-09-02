import os
import re

import yaml
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()
CONFIG_FILE_PATH = "config.yaml"


class StoreConfig(BaseModel):
    access_key_id: str
    secret_access_key: str
    bucket_name: str
    bucket_endpoint: str
    runtime_env: str


class Configs(BaseModel):
    store: StoreConfig


config: Configs | None = None


def get_config() -> Configs:
    global config
    if config != None:
        return config
    with open(CONFIG_FILE_PATH) as config_file:
        content = config_file.read()
    pattern = re.compile(r"\$\{(\w+)\}")
    content = pattern.sub(lambda match: os.getenv(match.group(1), ""), content)
    data = yaml.safe_load(content)
    config = Configs(**data)
    return config
