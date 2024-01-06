from config.structures import ConfigBranch, ConfigBase


class DBConfig(ConfigBranch):
    type: str
    name: str

    connector: str | None = None
    host_and_port: str | None = None
    login: str | None = None
    password: str | None = None
    show_echo: bool = False
    pool_size: int | None = None
    max_overflow: int | None = None

    @property
    def uri(self) -> str:
        if self.type == "sqlite":
            return f"{self.type}+aiosqlite:///{self.name}"
        else:
            return (
                f"{self.type}+{self.connector}://"
                f"{self.login}:{self.password}@{self.host_and_port}/{self.name}"
            )


class Config(ConfigBase):
    """Connect config branches (class from ConfigBranch) here"""

    db: DBConfig
