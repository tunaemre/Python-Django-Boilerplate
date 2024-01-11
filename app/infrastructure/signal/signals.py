from django.dispatch import Signal

from common.cache.redis import init_redis
from common.logger.graylog import init_graylog

global_ready = Signal()


def _global_ready_observers() -> None:
    global_ready.connect(init_redis)
    global_ready.connect(init_graylog)


_global_ready_observers()
