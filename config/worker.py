from typing import Optional, Any

from environ import Env

from config.base.base_config import BaseConfig


class GlobalConfig(BaseConfig):

    def __init__(self, env: Env) -> None:
        super().__init__(env)

        self.BROKER_URL: str = env.str('BROKER_URL')  # amqp://username:password@0.0.0.0:5672

        self.AUTH0_M2M_CLIENT_ID: str = env.str('AUTH0_M2M_CLIENT_ID')
        self.AUTH0_M2M_CLIENT_SECRET: str = env.str('AUTH0_M2M_CLIENT_SECRET')

        self.BEAT_CHECK_EXPIRED_TODOS_INTERVAL: int = env.int('BEAT_CHECK_EXPIRED_TODOS_INTERVAL', default=1)
        self.EXPIRE_TIME_OF_TASKS: int = env.int('EXPIRE_TIME_OF_TASKS', default=60)

        self.TODO_API_URL: str = env.str('TODO_API_URL')
        self.MAIL_SERVICE_API_KEY: str = env.str('MAIL_SERVICE_API_KEY')


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
