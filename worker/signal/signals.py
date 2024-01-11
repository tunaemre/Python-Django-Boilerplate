from django.dispatch import Signal

from common.cache.redis import init_redis

global_ready = Signal()


def _global_ready_observers() -> None:
    global_ready.connect(init_redis)


_global_ready_observers()
