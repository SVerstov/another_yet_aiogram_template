import os
import tomllib
from dataclasses import dataclass
from pathlib import Path
from pydantic import BaseModel

from pydantic.functional_validators import model_validator
from loguru import logger


class ConfigBranch(BaseModel):
    """
    Base class for config branches with automatic loading
     of parameters based on annotations.
    Also takes data from environment variables,
    if in the config the variable looks like this: $SOME_ENV_VAR
    """

    @model_validator(mode="before")
    @classmethod
    def check_data(cls, data: dict) -> dict:
        for key, value in data.items():
            if isinstance(value, str) and value.startswith("$"):
                param_name = value.lstrip("$")
                logger.debug(
                    f"{cls.__name__}: Getting '{param_name}' from environment variables"
                )
                value = os.getenv(param_name)
                if value is None:
                    logger.warning(f"Can't load '{param_name}' from environment")
                data[key] = os.getenv(param_name)
            if key not in cls.model_fields:
                logger.warning(f"{cls.__name__}: unknown parameter '{key}'")
        return data

    @model_validator(mode="after")
    def launch_after_load(self):
        self.after_load()
        return self

    def after_load(self):
        # Override if additional actions with the config are needed
        pass


@dataclass
class ConfigBase:
    conf_path: Path = Path("config/config.toml")

    def __init__(self):
        with open(self.conf_path, "rb") as f:
            config_dct = tomllib.load(f)

        for attr, config_branch in self.__annotations__.items():
            if issubclass(config_branch, ConfigBranch):
                self.__setattr__(attr, config_branch.model_validate(config_dct[attr]))
        self.after_load()
        logger.info("Config loaded!")

    def after_load(self):
        # Override if additional actions with the config are needed
        pass
