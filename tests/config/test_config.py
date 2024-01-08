from typing import Any

import pytest
import os

from pydantic import ValidationError

from config.structures import ConfigBase
from config import DBConfig


class Config(ConfigBase):
    """mini conf class for tests"""

    db: DBConfig


class TestConfig:
    db_vars = [
        ("type", "sqlite"),
        ("name", "db/db.sqlite"),
        ("login", None),
        ("password", "SecretPassword"),
        ("show_echo", True),
        ("pool_size", 10),
    ]

    @pytest.fixture
    def config(self, tmp_path) -> DBConfig:
        os.environ["TEST_DBPASS"] = "SecretPassword"
        tmp_file = tmp_path / "config.toml"
        with open(tmp_file, "w") as f:
            f.write(
                """
                [db]\n
                type = "sqlite"\n
                name = "db/db.sqlite"\n
                show_echo = true\n
                login =  "$LOGIN"\n
                password = "$TEST_DBPASS"\n
                pool_size = 10
                """
            )

        config = Config(conf_path=tmp_file)
        yield config

        del os.environ["TEST_DBPASS"]
        tmp_file.unlink(missing_ok=True)

    @pytest.mark.parametrize(["var", "expected"], db_vars)
    def test_db_vars(self, config: Config, var: str, expected: Any):
        assert getattr(config.db, var) == expected

    def test_invalid_login_type(self, tmp_path):
        tmp_file = tmp_path / "config_invalid.toml"
        with open(tmp_file, "w") as f:
            f.write(
                "[db]\n"
                "type = 'sqlite'\n"
                "name = 'db/db.sqlite'\n"
                "login = ['wrong', 'type']\n"  # Invalid type for login
            )

        with pytest.raises(ValidationError):
            # Expect Pydantic to raise a ValidationError
            Config(conf_path=tmp_file)
