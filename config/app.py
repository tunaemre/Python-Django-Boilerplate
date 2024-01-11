from typing import Optional, Any

from environ import Env

from config.base.base_config import BaseConfig


class GlobalConfig(BaseConfig):

    def __init__(self, env: Env) -> None:
        super().__init__(env)

        self.MYSQL_HOST: str = env.str('MYSQL_HOST')
        self.MYSQL_PORT: int = env.int('MYSQL_PORT')
        self.MYSQL_USERNAME: str = env.str('MYSQL_USERNAME')
        self.MYSQL_PASSWORD: str = env.str('MYSQL_PASSWORD')
        self.MYSQL_DB_NAME: str = env.str('MYSQL_DB_NAME')
        self.MYSQL_DB_CHARSET: str = env.str('MYSQL_DB_CHARSET', default='utf8mb4')

        self.SWAGGER_USERNAME: Optional[str] = env.str('SWAGGER_USERNAME', default=None)
        self.SWAGGER_PASSWORD: Optional[str] = env.str('SWAGGER_PASSWORD', default=None)


class _ConfigManagerMeta(type):
    def __enter__(cls) -> GlobalConfig:
        return cls.get_config()  # type: ignore

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        pass


class _ConfigManager(metaclass=_ConfigManagerMeta):
    __config: Optional[GlobalConfig] = None

    @classmethod
    def get_config(cls) -> GlobalConfig:
        if not cls.__config:
            env = Env()
            cls.__config = GlobalConfig(env)
        return cls.__config
