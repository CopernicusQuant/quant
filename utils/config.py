from typing import Any

import yaml

_cfg: dict[str, Any] = {}  # Singleton


def load_config(config_path: str = "config/config.yaml") -> dict[str, Any]:
    # Load yaml config
    global _cfg
    if len(_cfg) > 0:
        return _cfg
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            _cfg = yaml.safe_load(f)
        return _cfg
    except FileNotFoundError:
        raise FileNotFoundError(f"Failed to find config file: {config_path}")
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid config file format: {e}")
