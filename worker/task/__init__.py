from typing import Any

from celery.signals import after_setup_logger

from common.logger.graylog import init_graylog
from config import worker_config_manager


@after_setup_logger.connect
def celery_after_setup_logger(**kwargs: Any) -> None:
    init_graylog(worker_config_manager.get_config())


from worker.task import beats  # NOQA
from worker.task.status import tasks as status_tasks  # NOQA
from worker.task.mail import tasks as mail_tasks  # NOQA
