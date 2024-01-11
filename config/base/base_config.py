from __future__ import annotations

from typing import Optional
import logging

from environ import Env


class BaseConfig:

    def __init__(self, env: Env) -> None:
        """Secrets"""
        self.GRAYLOG_IP: Optional[str] = env.str('GRAYLOG_IP', default=None)
        self.GRAYLOG_PORT: Optional[int] = env.int('GRAYLOG_PORT', default=None)
        self.AUTH0_DOMAIN: str = env.str('AUTH0_DOMAIN')
        self.AUTH0_AUDIENCE: str = env.str('AUTH0_AUDIENCE')
        self.REDIS_HOST: str = env.str('REDIS_HOST')
        self.REDIS_PORT: int = env.int('REDIS_PORT')
        self.REDIS_PASSWORD: Optional[str] = env.str('REDIS_PASSWORD', default=None)
        self.REDIS_DB: int = env.int('REDIS_DB', default=0)

        """Configurations"""
        self.ENABLE_GRAYLOG: bool = env.bool('ENABLE_GRAYLOG', default=False)
        self.GRAYLOG_LOGGING_LEVEL: int = env.int('GRAYLOG_LOGGING_LEVEL', default=logging.INFO)
