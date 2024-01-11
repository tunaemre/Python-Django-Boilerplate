import os
from datetime import timedelta
from typing import Dict, Any

from celery import Celery

from config import worker_config_manager
from worker.signal.signals import global_ready

project_slug = 'boilerplate'

# Worker config instance
_worker_config = worker_config_manager.get_config()

_worker_concurrency = int(os.getenv('WORKER_CONCURRENCY', 0))
if _worker_concurrency == 0:
    import multiprocessing

    _worker_concurrency = multiprocessing.cpu_count()

config = {
    'task_ignore_result': True,
    'worker_concurrency': _worker_concurrency,
    'worker_disable_rate_limits': True,
    'worker_hijack_root_logger': True
}

celery = Celery('tasks', broker=_worker_config.BROKER_URL)
celery.conf.update(**config)

# task_queues must be defined in consumer
celery.conf.task_queues = {
    f'{project_slug}:beat_queue': {
        'queue_arguments': {'x-queue-mode': 'lazy'}
    },
    f'{project_slug}:status_queue': {
        'queue_arguments': {'x-queue-mode': 'lazy'}
    },
    f'{project_slug}:mail_queue': {
        'queue_arguments': {'x-queue-mode': 'lazy'}
    }
}

# task_routes of tasks that called from a worker must be defined in consumer
celery.conf.task_routes = [
    {'worker.task.beats.*': {'queue': f'{project_slug}:beat_queue'}},
    {'worker.task.status.tasks.*': {'queue': f'{project_slug}:status_queue'}},
    {'worker.task.mail.tasks.*': {'queue': f'{project_slug}:mail_queue'}}
]


def __prepare_beat_schedule() -> Dict[str, Any]:
    schedule: Dict[str, Any] = {
        'beat_check_expired_todos': {
            'task': 'worker.task.beats.beat_check_expired_todos',
            'schedule': timedelta(minutes=_worker_config.BEAT_CHECK_EXPIRED_TODOS_INTERVAL),
            'options': {'expires': _worker_config.EXPIRE_TIME_OF_TASKS}
        }
    }
    return schedule


celery.conf.beat_schedule = __prepare_beat_schedule()

import worker.task  # NOQA


# Send global ready signal
global_ready.send(_worker_config)
