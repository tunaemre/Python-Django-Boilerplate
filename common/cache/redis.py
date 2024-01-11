from typing import Optional, Any

from redis.client import Redis

from config import get_environment
from config.base.base_config import BaseConfig

_redis: Optional[Redis] = None


def init_redis(sender: BaseConfig, **kwargs: Any) -> None:
    assert isinstance(sender, BaseConfig), 'Method init_redis need a config instance as sender.'
    global _redis
    if _redis is not None:
        return

    env = get_environment()
    if env not in ('test', 'local'):
        # Redis password must be provided
        assert sender.REDIS_PASSWORD, 'Redis password must be provided.'

    _redis = Redis(
        host=sender.REDIS_HOST,
        port=sender.REDIS_PORT,
        password=sender.REDIS_PASSWORD,
        db=sender.REDIS_DB,
        decode_responses=True)


def redis() -> Redis:
    assert _redis is not None, 'Redis not initialized.'
    return _redis
