import pickle
from typing import Generic, Optional

from redis import Redis

from app.infrastructure.repository.base import BaseModelType
from common.cache.redis import redis


class CacheRepository(Generic[BaseModelType]):
    _default_cache_ttl = 10 * 60  # 10 minutes in seconds

    @staticmethod
    def _redis() -> Redis:
        return redis()

    @staticmethod
    def set_cache(key: str, model: BaseModelType) -> None:
        dump = pickle.dumps(model)
        dump_hex = dump.hex()
        CacheRepository._redis().set(key, dump_hex, ex=CacheRepository._default_cache_ttl)

    @staticmethod
    def get_cache(key: str) -> Optional[BaseModelType]:
        dump_hex = CacheRepository._redis().get(key)
        if not dump_hex:
            return None
        dump = bytes.fromhex(dump_hex)
        model = pickle.loads(dump)
        return model

    @staticmethod
    def invalidate_cache(key: str) -> None:
        CacheRepository._redis().delete(key)
